# Few-Shot Voice Cloning UI Implementation Guide

## Status

✅ **Completed:**
- Task #1: Python training service (`training_service.py`)
- Task #2: Rust training manager (`training_manager.rs`)
- Task #6: Voice data model updated (added `VoiceSource::Trained`)
- Task #7: Training helper functions

⚠️ **Remaining:**
- Task #3: Add UI tab switcher (Express/Pro modes)
- Task #4: Implement long-form audio recording (3-10 min)
- Task #5: Create training progress UI components
- Task #8: Testing

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ voice_clone_modal.rs (UI)                                    │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ CloneMode: Express | Pro                                 ││
│ │ ┌────────────┐  ┌──────────────────────────────────────┐││
│ │ │ Express    │  │ Pro Mode (Few-Shot Training)         │││
│ │ │ (Zero-shot)│  │ ┌──────────────────────────────────┐ │││
│ │ │            │  │ │ Long Recording (3-10 min)        │ │││
│ │ │ 3-10s audio│  │ │ + Voice Name                     │ │││
│ │ │ + prompt   │  │ │ + Language                       │ │││
│ │ └────────────┘  │ │ ↓                                │ │││
│ │                 │ │ [Start Training]                 │ │││
│ │                 │ │ ↓                                │ │││
│ │                 │ │ Training Progress UI             │ │││
│ │                 │ │ - Stage: "Slicing audio"         │ │││
│ │                 │ │ - Progress: Step 3/7             │ │││
│ │                 │ │ - Log scroll view                │ │││
│ │                 │ │ - [Cancel] button                │ │││
│ │                 │ └──────────────────────────────────┘ │││
│ │                 └──────────────────────────────────────┘││
│ └──────────────────────────────────────────────────────────┘│
│                            ↓                                 │
│                   TrainingManager (Rust)                     │
│                            ↓                                 │
│              training_service.py (Python subprocess)         │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Steps

### Step 1: Add CloneMode enum to VoiceCloneModal

```rust
// Add to voice_clone_modal.rs near top

#[derive(Clone, Debug, PartialEq)]
pub enum CloneMode {
    Express,  // Zero-shot (existing)
    Pro,      // Few-shot training (new)
}

impl Default for CloneMode {
    fn default() -> Self {
        Self::Express
    }
}
```

### Step 2: Extend VoiceCloneModal struct

```rust
#[derive(Live, LiveHook, Widget)]
pub struct VoiceCloneModal {
    #[deref]
    view: View,

    // ... existing fields ...

    // NEW FIELDS for Pro mode
    #[rust]
    clone_mode: CloneMode,

    #[rust]
    training_manager: Option<Arc<crate::training_manager::TrainingManager>>,

    #[rust]
    training_progress: crate::training_manager::TrainingProgress,

    #[rust]
    recording_for_training: bool,

    #[rust]
    training_audio_file: Option<PathBuf>,

    #[rust]
    training_audio_samples: Vec<f32>,

    #[rust]
    max_training_duration: f32,  // 600 seconds = 10 minutes

    #[rust]
    training_recording_start: Option<std::time::Instant>,
}

impl LiveHook for VoiceCloneModal {
    fn after_new_from_doc(&mut self, _cx: &mut Cx) {
        // Initialize training manager
        self.training_manager = Some(Arc::new(crate::training_manager::TrainingManager::new()));
    }
}
```

### Step 3: Add Mode Tab Switcher to live_design!

Insert after header, before body in the modal_content:

```rust
// Mode tabs
mode_tabs = <View> {
    width: Fill, height: Fit
    flow: Right
    spacing: 0
    padding: {left: 24, right: 24, top: 16, bottom: 0}

    show_bg: true
    draw_bg: {
        instance dark_mode: 0.0
        fn pixel(self) -> vec4 {
            return mix((SLATE_50), (SLATE_700), self.dark_mode);
        }
    }

    express_tab = <ModeTabButton> {
        text: "Express Mode"
        draw_bg: { active: 1.0 }
        draw_text: { active: 1.0 }
    }

    pro_tab = <ModeTabButton> {
        text: "Pro Mode (Training)"
        draw_bg: { active: 0.0 }
        draw_text: { active: 0.0 }
    }
}

// Define ModeTabButton component
ModeTabButton = <Button> {
    width: Fit, height: 44
    padding: {left: 24, right: 24}

    draw_bg: {
        instance dark_mode: 0.0
        instance hover: 0.0
        instance active: 0.0

        fn pixel(self) -> vec4 {
            let sdf = Sdf2d::viewport(self.pos * self.rect_size);

            // Background
            let base = mix((SLATE_50), (SLATE_700), self.dark_mode);
            let active_bg = mix((WHITE), (SLATE_800), self.dark_mode);
            let bg = mix(base, active_bg, self.active);
            sdf.box(0., 0., self.rect_size.x, self.rect_size.y, 0.0);
            sdf.fill(bg);

            // Bottom border (active indicator)
            if self.active > 0.5 {
                let border_color = mix((PRIMARY_500), (PRIMARY_400), self.dark_mode);
                sdf.move_to(0., self.rect_size.y);
                sdf.line_to(self.rect_size.x, self.rect_size.y);
                sdf.stroke(border_color, 3.0);
            }

            return sdf.result;
        }
    }

    draw_text: {
        instance dark_mode: 0.0
        instance active: 0.0
        text_style: <FONT_SEMIBOLD>{ font_size: 13.0 }
        fn get_color(self) -> vec4 {
            let inactive = mix((SLATE_600), (SLATE_400), self.dark_mode);
            let active_color = mix((TEXT_PRIMARY), (TEXT_PRIMARY_DARK), self.dark_mode);
            return mix(inactive, active_color, self.active);
        }
    }
}
```

### Step 4: Split body into express_mode_content and pro_mode_content

Wrap existing body content:

```rust
body = <View> {
    width: Fill, height: Fit
    flow: Down
    spacing: 0

    // EXPRESS MODE CONTENT (existing fields)
    express_mode_content = <View> {
        width: Fill, height: Fit
        flow: Down
        padding: {left: 24, right: 24, top: 16, bottom: 16}
        spacing: 16
        visible: true

        // Move existing fields here:
        // - file_selector
        // - prompt_text_input
        // - voice_name_input
        // - language_selector
        // - progress_log
    }

    // PRO MODE CONTENT (new training UI)
    pro_mode_content = <View> {
        width: Fill, height: Fit
        flow: Down
        padding: {left: 24, right: 24, top: 16, bottom: 16}
        spacing: 16
        visible: false

        // Long recording section
        training_recording_section = <View> {
            width: Fill, height: Fit
            flow: Down
            spacing: 12

            label = <Label> {
                width: Fill, height: Fit
                draw_text: {
                    instance dark_mode: 0.0
                    text_style: <FONT_SEMIBOLD>{ font_size: 12.0 }
                    fn get_color(self) -> vec4 {
                        return mix((TEXT_PRIMARY), (TEXT_PRIMARY_DARK), self.dark_mode);
                    }
                }
                text: "Training Audio Recording"
            }

            instruction = <Label> {
                width: Fill, height: Fit
                draw_text: {
                    instance dark_mode: 0.0
                    text_style: { font_size: 11.0 }
                    fn get_color(self) -> vec4 {
                        return mix((TEXT_SECONDARY), (TEXT_SECONDARY_DARK), self.dark_mode);
                    }
                }
                text: "Record 3-10 minutes of continuous speech. Speak clearly with varied sentences for best results."
            }

            record_row = <View> {
                width: Fill, height: Fit
                flow: Right
                spacing: 12
                align: {y: 0.5}

                record_btn = <Button> {
                    width: 48, height: 48
                    // Large record button (red pulsing when recording)
                    draw_bg: {
                        instance dark_mode: 0.0
                        instance recording: 0.0
                        instance pulse: 0.0

                        fn pixel(self) -> vec4 {
                            let sdf = Sdf2d::viewport(self.pos * self.rect_size);
                            sdf.circle(24.0, 24.0, 22.0);

                            if self.recording > 0.5 {
                                // Recording state: pulsing red
                                let pulse_intensity = 0.8 + 0.2 * sin(self.pulse * 6.28);
                                let color = mix((RED_500), (RED_600), pulse_intensity);
                                sdf.fill(color);

                                // Stop square icon
                                sdf.rect(18.0, 18.0, 12.0, 12.0);
                                sdf.fill((WHITE));
                            } else {
                                // Idle state: gray with red mic
                                let bg = mix((SLATE_100), (SLATE_700), self.dark_mode);
                                sdf.fill(bg);

                                // Microphone icon
                                sdf.box(20.0, 14.0, 8.0, 12.0, 4.0);
                                sdf.fill((RED_500));
                            }

                            return sdf.result;
                        }
                    }
                }

                recording_info = <View> {
                    width: Fill, height: Fit
                    flow: Down
                    spacing: 4

                    duration_label = <Label> {
                        width: Fill, height: Fit
                        draw_text: {
                            instance dark_mode: 0.0
                            text_style: <FONT_SEMIBOLD>{ font_size: 14.0 }
                            fn get_color(self) -> vec4 {
                                return mix((TEXT_PRIMARY), (TEXT_PRIMARY_DARK), self.dark_mode);
                            }
                        }
                        text: "Click to start recording"
                    }

                    progress_label = <Label> {
                        width: Fill, height: Fit
                        draw_text: {
                            instance dark_mode: 0.0
                            text_style: { font_size: 11.0 }
                            fn get_color(self) -> vec4 {
                                return mix((TEXT_TERTIARY), (TEXT_TERTIARY_DARK), self.dark_mode);
                            }
                        }
                        text: "Target: 5-10 minutes"
                    }
                }
            }

            // Duration progress bar
            duration_bar = <View> {
                width: Fill, height: 6
                visible: false
                show_bg: true

                draw_bg: {
                    instance dark_mode: 0.0
                    instance progress: 0.0

                    fn pixel(self) -> vec4 {
                        let sdf = Sdf2d::viewport(self.pos * self.rect_size);

                        // Background bar
                        sdf.box(0., 0., self.rect_size.x, self.rect_size.y, 3.0);
                        let bg = mix((SLATE_200), (SLATE_600), self.dark_mode);
                        sdf.fill(bg);

                        // Progress bar
                        let progress_width = self.rect_size.x * self.progress;
                        sdf.box(0., 0., progress_width, self.rect_size.y, 3.0);

                        // Color gradient: green (3 min) -> yellow (7 min) -> red (10 min)
                        let color = mix((GREEN_500), (YELLOW_500), smoothstep(0.3, 0.7, self.progress));
                        let color = mix(color, (RED_500), smoothstep(0.7, 1.0, self.progress));
                        sdf.fill(color);

                        return sdf.result;
                    }
                }
            }
        }

        // Voice name + language (reuse from express mode)
        voice_name_input = <LabeledInput> {
            label = { text: "Voice Name" }
            input = { empty_text: "Enter a name for this trained voice..." }
        }

        language_selector = <LanguageSelector> {}

        // GPU warning
        gpu_warning = <View> {
            width: Fill, height: Fit
            padding: 12
            visible: false
            show_bg: true
            draw_bg: {
                instance dark_mode: 0.0
                border_radius: 6.0
                fn pixel(self) -> vec4 {
                    let sdf = Sdf2d::viewport(self.pos * self.rect_size);
                    sdf.box(0., 0., self.rect_size.x, self.rect_size.y, self.border_radius);
                    let bg = mix((AMBER_50), (AMBER_900), self.dark_mode);
                    sdf.fill(bg);
                    let border = mix((AMBER_200), (AMBER_600), self.dark_mode);
                    sdf.stroke(border, 1.0);
                    return sdf.result;
                }
            }

            message = <Label> {
                width: Fill, height: Fit
                draw_text: {
                    instance dark_mode: 0.0
                    text_style: { font_size: 11.0 }
                    fn get_color(self) -> vec4 {
                        return mix((AMBER_900), (AMBER_100), self.dark_mode);
                    }
                }
                text: "⚠️ No GPU detected. Training will be VERY slow (8-24 hours). Consider using a machine with CUDA GPU."
            }
        }

        // Training progress section (initially hidden)
        training_progress_section = <View> {
            width: Fill, height: Fit
            flow: Down
            spacing: 12
            visible: false

            stage_label = <Label> {
                width: Fill, height: Fit
                draw_text: {
                    instance dark_mode: 0.0
                    text_style: <FONT_SEMIBOLD>{ font_size: 13.0 }
                    fn get_color(self) -> vec4 {
                        return mix((TEXT_PRIMARY), (TEXT_PRIMARY_DARK), self.dark_mode);
                    }
                }
                text: "Training Status: Preparing..."
            }

            progress_bar = <View> {
                width: Fill, height: 8
                show_bg: true
                draw_bg: {
                    instance dark_mode: 0.0
                    instance progress: 0.0
                    border_radius: 4.0

                    fn pixel(self) -> vec4 {
                        let sdf = Sdf2d::viewport(self.pos * self.rect_size);

                        // Background
                        sdf.box(0., 0., self.rect_size.x, self.rect_size.y, self.border_radius);
                        let bg = mix((SLATE_200), (SLATE_600), self.dark_mode);
                        sdf.fill(bg);

                        // Progress
                        let progress_width = self.rect_size.x * self.progress;
                        sdf.box(0., 0., progress_width, self.rect_size.y, self.border_radius);
                        sdf.fill((PRIMARY_500));

                        return sdf.result;
                    }
                }
            }

            log_scroll = <ScrollYView> {
                width: Fill, height: 200
                show_bg: true
                draw_bg: {
                    instance dark_mode: 0.0
                    fn pixel(self) -> vec4 {
                        let sdf = Sdf2d::viewport(self.pos * self.rect_size);
                        sdf.box(0., 0., self.rect_size.x, self.rect_size.y, 4.0);
                        let bg = mix((SLATE_50), (SLATE_800), self.dark_mode);
                        sdf.fill(bg);
                        sdf.stroke(mix((SLATE_200), (SLATE_600), self.dark_mode), 1.0);
                        return sdf.result;
                    }
                }

                log_content = <Label> {
                    width: Fill, height: Fit
                    padding: {left: 10, right: 10, top: 8, bottom: 8}
                    draw_text: {
                        instance dark_mode: 0.0
                        text_style: { font_size: 11.0, line_spacing: 1.5, font: "courier" }
                        fn get_color(self) -> vec4 {
                            return mix((SLATE_600), (SLATE_300), self.dark_mode);
                        }
                    }
                    text: ""
                }
            }
        }
    }
}
```

### Step 5: Update footer with mode-specific buttons

```rust
footer = <View> {
    width: Fill, height: Fit
    padding: {left: 24, right: 24, top: 16, bottom: 20}
    flow: Right
    align: {x: 1.0, y: 0.5}
    spacing: 12

    show_bg: true
    draw_bg: {
        instance dark_mode: 0.0
        fn pixel(self) -> vec4 {
            return mix((SLATE_50), (SLATE_700), self.dark_mode);
        }
    }

    // Express mode buttons (existing)
    express_actions = <View> {
        width: Fit, height: Fit
        flow: Right
        spacing: 12
        visible: true

        cancel_btn = <ActionButton> {
            text: "Cancel"
            draw_bg: { primary: 0.0 }
            draw_text: { primary: 0.0 }
        }

        save_btn = <ActionButton> {
            text: "Save Voice"
            draw_bg: { primary: 1.0 }
            draw_text: { primary: 1.0 }
        }
    }

    // Pro mode buttons (new)
    pro_actions = <View> {
        width: Fit, height: Fit
        flow: Right
        spacing: 12
        visible: false

        cancel_training_btn = <ActionButton> {
            text: "Cancel Training"
            draw_bg: { primary: 0.0 }
            draw_text: { primary: 0.0 }
            visible: false  // Show only when training is running
        }

        start_training_btn = <ActionButton> {
            text: "Start Training"
            draw_bg: { primary: 1.0 }
            draw_text: { primary: 1.0 }
        }
    }
}
```

### Step 6: Implement event handlers

```rust
impl MatchEvent for VoiceCloneModal {
    fn handle_actions(&mut self, cx: &mut Cx, actions: &Actions, scope: &mut Scope) {
        // ... existing code ...

        // Mode tab switching
        if self.button(id!(mode_tabs.express_tab)).clicked(&actions) {
            self.switch_to_mode(cx, CloneMode::Express);
        }

        if self.button(id!(mode_tabs.pro_tab)).clicked(&actions) {
            self.switch_to_mode(cx, CloneMode::Pro);
        }

        // Pro mode: Long recording
        if self.clone_mode == CloneMode::Pro {
            if self.button(id!(pro_mode_content.training_recording_section.record_row.record_btn))
                .clicked(&actions)
            {
                self.toggle_training_recording(cx);
            }

            // Start training button
            if self.button(id!(footer.pro_actions.start_training_btn)).clicked(&actions) {
                self.start_training(cx, scope);
            }

            // Cancel training button
            if self.button(id!(footer.pro_actions.cancel_training_btn)).clicked(&actions) {
                self.cancel_training(cx);
            }

            // Poll training progress (call in handle_event)
            self.poll_training_progress(cx);
        }
    }
}

impl VoiceCloneModal {
    fn switch_to_mode(&mut self, cx: &mut Cx, mode: CloneMode) {
        if self.clone_mode == mode {
            return;
        }

        self.clone_mode = mode;

        match mode {
            CloneMode::Express => {
                // Update tab visuals
                self.button(id!(mode_tabs.express_tab))
                    .apply_over(cx, live! { draw_bg: { active: 1.0 }, draw_text: { active: 1.0 } });
                self.button(id!(mode_tabs.pro_tab))
                    .apply_over(cx, live! { draw_bg: { active: 0.0 }, draw_text: { active: 0.0 } });

                // Show/hide content
                self.view(id!(body.express_mode_content)).set_visible(true);
                self.view(id!(body.pro_mode_content)).set_visible(false);
                self.view(id!(footer.express_actions)).set_visible(true);
                self.view(id!(footer.pro_actions)).set_visible(false);
            }

            CloneMode::Pro => {
                self.button(id!(mode_tabs.express_tab))
                    .apply_over(cx, live! { draw_bg: { active: 0.0 }, draw_text: { active: 0.0 } });
                self.button(id!(mode_tabs.pro_tab))
                    .apply_over(cx, live! { draw_bg: { active: 1.0 }, draw_text: { active: 1.0 } });

                self.view(id!(body.express_mode_content)).set_visible(false);
                self.view(id!(body.pro_mode_content)).set_visible(true);
                self.view(id!(footer.express_actions)).set_visible(false);
                self.view(id!(footer.pro_actions)).set_visible(true);

                // Check GPU availability
                self.check_gpu_availability(cx);
            }
        }

        self.redraw(cx);
    }

    fn toggle_training_recording(&mut self, cx: &mut Cx) {
        if self.recording_for_training {
            self.stop_training_recording(cx);
        } else {
            self.start_training_recording(cx);
        }
    }

    fn start_training_recording(&mut self, cx: &mut Cx) {
        self.recording_for_training = true;
        self.training_audio_samples.clear();
        self.training_recording_start = Some(std::time::Instant::now());
        self.max_training_duration = 600.0; // 10 minutes

        // Update UI
        self.label(id!(pro_mode_content.training_recording_section.record_row.recording_info.duration_label))
            .set_text("Recording... 0:00 / 10:00");

        self.view(id!(pro_mode_content.training_recording_section.duration_bar))
            .set_visible(true);

        self.button(id!(pro_mode_content.training_recording_section.record_row.record_btn))
            .apply_over(cx, live! { draw_bg: { recording: 1.0 } });

        // Start CPAL recording (reuse existing audio capture logic)
        self.start_audio_capture();

        self.redraw(cx);
    }

    fn stop_training_recording(&mut self, cx: &mut Cx) {
        self.recording_for_training = false;

        // Stop audio capture
        self.stop_audio_capture();

        // Calculate duration
        let duration = if let Some(start) = self.training_recording_start {
            start.elapsed().as_secs_f32()
        } else {
            0.0
        };

        // Validate duration
        if duration < 180.0 {
            self.add_training_log(
                cx,
                &format!("[ERROR] Recording too short: {:.1}s (minimum: 180s)", duration),
            );
            self.training_audio_samples.clear();
            return;
        }

        // Save to temp file
        let temp_dir = std::env::temp_dir();
        let temp_file = temp_dir.join(format!(
            "training_audio_{}.wav",
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs()
        ));

        // Write WAV file
        if let Err(e) = self.write_wav_file(&temp_file, &self.training_audio_samples, 48000) {
            self.add_training_log(cx, &format!("[ERROR] Failed to save audio: {}", e));
            return;
        }

        self.training_audio_file = Some(temp_file.clone());
        self.add_training_log(
            cx,
            &format!("[SUCCESS] Recording saved ({:.1}s)", duration),
        );

        // Enable start training button
        self.button(id!(footer.pro_actions.start_training_btn))
            .set_enabled(true);

        // Update UI
        self.button(id!(pro_mode_content.training_recording_section.record_row.record_btn))
            .apply_over(cx, live! { draw_bg: { recording: 0.0 } });

        self.redraw(cx);
    }

    fn start_training(&mut self, cx: &mut Cx, scope: &mut Scope) {
        // Validate inputs
        let voice_name = self.text_input(id!(pro_mode_content.voice_name_input.input)).text();
        if voice_name.is_empty() {
            self.add_training_log(cx, "[ERROR] Voice name is required");
            return;
        }

        let Some(audio_file) = &self.training_audio_file else {
            self.add_training_log(cx, "[ERROR] No training audio recorded");
            return;
        };

        let language = self.selected_language.clone();
        let voice_id = voice_persistence::generate_voice_id(&voice_name);

        // Show progress section
        self.view(id!(pro_mode_content.training_progress_section))
            .set_visible(true);

        // Show cancel button, hide start button
        self.button(id!(footer.pro_actions.cancel_training_btn))
            .set_visible(true);
        self.button(id!(footer.pro_actions.start_training_btn))
            .set_visible(false);

        // Start training via manager
        let manager = self.training_manager.as_ref().unwrap();
        if !manager.start_training(voice_id, voice_name, audio_file.clone(), language) {
            self.add_training_log(cx, "[ERROR] Failed to start training");
            return;
        }

        self.add_training_log(cx, "[INFO] Training started...");
        self.add_training_log(cx, "[INFO] This will take 30-120 minutes. Do not close the application.");

        self.redraw(cx);
    }

    fn cancel_training(&mut self, cx: &mut Cx) {
        if let Some(ref manager) = self.training_manager {
            manager.cancel_training();
            self.add_training_log(cx, "[INFO] Cancelling training (may take a few seconds)...");
        }
    }

    fn poll_training_progress(&mut self, cx: &mut Cx) {
        let Some(ref manager) = self.training_manager else {
            return;
        };

        let progress = manager.get_progress();

        // Only update if changed
        if progress.last_updated > self.training_progress.last_updated {
            self.training_progress = progress.clone();
            self.update_training_ui(cx, &progress);
        }
    }

    fn update_training_ui(&mut self, cx: &mut Cx, progress: &crate::training_manager::TrainingProgress) {
        use crate::training_manager::TrainingStatus;

        // Update stage label
        self.label(id!(pro_mode_content.training_progress_section.stage_label))
            .set_text(&format!(
                "Step {} of {}: {}",
                progress.current_step, progress.total_steps, progress.current_stage
            ));

        // Update progress bar
        let progress_pct = if progress.total_steps > 0 {
            progress.current_step as f32 / progress.total_steps as f32
        } else {
            0.0
        };

        self.view(id!(pro_mode_content.training_progress_section.progress_bar))
            .apply_over(cx, live! { draw_bg: { progress: (progress_pct) } });

        // Update log content (show last 100 lines)
        let log_text = progress
            .log_lines
            .iter()
            .rev()
            .take(100)
            .rev()
            .cloned()
            .collect::<Vec<_>>()
            .join("\n");

        self.label(id!(pro_mode_content.training_progress_section.log_scroll.log_content))
            .set_text(&log_text);

        // Handle training completion
        match &progress.status {
            TrainingStatus::Completed {
                gpt_weights,
                sovits_weights,
                reference_audio,
                reference_text,
            } => {
                self.on_training_completed(
                    cx,
                    gpt_weights.clone(),
                    sovits_weights.clone(),
                    reference_audio.clone(),
                    reference_text.clone(),
                );
            }
            TrainingStatus::Failed { error } => {
                self.add_training_log(cx, &format!("[ERROR] Training failed: {}", error));
                // Re-enable start button
                self.button(id!(footer.pro_actions.start_training_btn))
                    .set_visible(true);
                self.button(id!(footer.pro_actions.cancel_training_btn))
                    .set_visible(false);
            }
            TrainingStatus::Cancelled => {
                self.add_training_log(cx, "[INFO] Training cancelled");
                // Re-enable start button
                self.button(id!(footer.pro_actions.start_training_btn))
                    .set_visible(true);
                self.button(id!(footer.pro_actions.cancel_training_btn))
                    .set_visible(false);
            }
            _ => {}
        }

        self.redraw(cx);
    }

    fn on_training_completed(
        &mut self,
        cx: &mut Cx,
        gpt_weights: PathBuf,
        sovits_weights: PathBuf,
        reference_audio: PathBuf,
        reference_text: String,
    ) {
        use crate::voice_data::{Voice, VoiceCategory, VoiceSource};

        let voice_name = self.text_input(id!(pro_mode_content.voice_name_input.input)).text();
        let voice_id = voice_persistence::generate_voice_id(&voice_name);

        // Create new trained voice entry
        let new_voice = Voice {
            id: voice_id.clone(),
            name: voice_name.clone(),
            description: format!("Custom trained voice (Few-Shot)"),
            category: VoiceCategory::Character,
            language: self.selected_language.clone(),
            source: VoiceSource::Trained,
            reference_audio_path: Some(reference_audio.to_string_lossy().to_string()),
            prompt_text: Some(reference_text),
            gpt_weights: Some(gpt_weights.to_string_lossy().to_string()),
            sovits_weights: Some(sovits_weights.to_string_lossy().to_string()),
            created_at: Some(
                std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_secs(),
            ),
            preview_audio: Some(reference_audio.to_string_lossy().to_string()),
        };

        // Save to custom voices config
        if let Err(e) = voice_persistence::add_custom_voice(new_voice.clone()) {
            self.add_training_log(cx, &format!("[ERROR] Failed to save voice: {}", e));
            return;
        }

        self.add_training_log(cx, "[SUCCESS] Voice saved successfully!");

        // Emit action to notify parent screen
        cx.widget_action(
            self.widget_uid(),
            &scope.path,
            VoiceCloneModalAction::VoiceCreated(new_voice),
        );

        // Show success message
        self.button(id!(footer.pro_actions.start_training_btn))
            .set_visible(true);
        self.button(id!(footer.pro_actions.cancel_training_btn))
            .set_visible(false);
    }

    fn check_gpu_availability(&mut self, cx: &mut Cx) {
        // Check if CUDA is available (simplified check)
        let has_gpu = std::process::Command::new("python")
            .arg("-c")
            .arg("import torch; print(torch.cuda.is_available())")
            .output()
            .map(|out| String::from_utf8_lossy(&out.stdout).trim() == "True")
            .unwrap_or(false);

        if !has_gpu {
            // Show warning
            self.view(id!(pro_mode_content.gpu_warning)).set_visible(true);
        } else {
            self.view(id!(pro_mode_content.gpu_warning)).set_visible(false);
        }
    }

    fn add_training_log(&mut self, cx: &mut Cx, message: &str) {
        self.training_progress.log_lines.push(message.to_string());

        let log_text = self.training_progress
            .log_lines
            .iter()
            .rev()
            .take(100)
            .rev()
            .cloned()
            .collect::<Vec<_>>()
            .join("\n");

        self.label(id!(pro_mode_content.training_progress_section.log_scroll.log_content))
            .set_text(&log_text);

        self.redraw(cx);
    }
}
```

## Testing Checklist

- [ ] Tab switching works smoothly
- [ ] Long recording (5-10 min) completes without issues
- [ ] Training progress updates in real-time
- [ ] Log output is readable and informative
- [ ] Cancel button works at any stage
- [ ] Trained voice is saved and loadable
- [ ] TTS inference works with trained model
- [ ] Dark mode styling looks correct
- [ ] GPU detection works correctly
- [ ] CPU fallback works (with warning)

## Next Steps

1. Apply the changes from this guide to `voice_clone_modal.rs`
2. Test locally with sample audio
3. Verify training pipeline end-to-end
4. Test trained voice synthesis
5. Polish UI animations and error handling
