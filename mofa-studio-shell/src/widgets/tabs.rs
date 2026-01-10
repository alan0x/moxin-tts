//! Tab Widgets - Reusable tab bar components for MoFA Studio
//!
//! This module provides tab widgets for the shell's tab overlay system:
//! - `TabWidget` - Closeable tab with label
//! - `HomeTabWidget` - Non-closeable home tab with icon
//! - `TabBar` - Container for tab widgets

use makepad_widgets::*;

live_design! {
    use link::theme::*;
    use link::shaders::*;
    use link::widgets::*;

    // Import fonts and colors from shared theme
    use mofa_widgets::theme::FONT_MEDIUM;
    use mofa_widgets::theme::SLATE_200;
    use mofa_widgets::theme::SLATE_400;
    use mofa_widgets::theme::SLATE_500;
    use mofa_widgets::theme::SLATE_600;
    use mofa_widgets::theme::SLATE_700;
    use mofa_widgets::theme::SLATE_800;
    use mofa_widgets::theme::WHITE;
    use mofa_widgets::theme::TRANSPARENT;
    use mofa_widgets::theme::ACCENT_BLUE;

    // Tab widget - individual tab in tab bar
    pub TabWidget = <View> {
        width: Fit, height: 36
        flow: Right
        align: {y: 0.5}
        padding: {left: 12, right: 4, top: 0, bottom: 0}
        cursor: Hand
        show_bg: true
        draw_bg: {
            instance active: 0.0
            instance dark_mode: 0.0
            fn pixel(self) -> vec4 {
                let sdf = Sdf2d::viewport(self.pos * self.rect_size);
                sdf.box(0., 0., self.rect_size.x, self.rect_size.y + 4.0, 6.0);
                let light_inactive = (SLATE_200);
                let light_active = (WHITE);
                let dark_inactive = (SLATE_700);
                let dark_active = (SLATE_800);
                let inactive = mix(light_inactive, dark_inactive, self.dark_mode);
                let active_color = mix(light_active, dark_active, self.dark_mode);
                let color = mix(inactive, active_color, self.active);
                sdf.fill(color);
                return sdf.result;
            }
        }

        tab_label = <Label> {
            text: "Tab"
            margin: {right: 8}
            draw_text: {
                instance active: 0.0
                instance dark_mode: 0.0
                text_style: <FONT_MEDIUM>{ font_size: 11.0 }
                fn get_color(self) -> vec4 {
                    let light_inactive = (SLATE_500);
                    let light_active = (SLATE_800);
                    let dark_inactive = (SLATE_400);
                    let dark_active = (SLATE_200);
                    let inactive = mix(light_inactive, dark_inactive, self.dark_mode);
                    let active_color = mix(light_active, dark_active, self.dark_mode);
                    return mix(inactive, active_color, self.active);
                }
            }
        }

        close_btn = <View> {
            width: 18, height: 18
            cursor: Hand
            show_bg: true
            draw_bg: {
                instance hover: 0.0
                instance dark_mode: 0.0
                fn pixel(self) -> vec4 {
                    let sdf = Sdf2d::viewport(self.pos * self.rect_size);
                    let c = self.rect_size * 0.5;
                    sdf.circle(c.x, c.y, 8.0);
                    let hover_bg = mix((SLATE_200), (SLATE_600), self.dark_mode);
                    sdf.fill(mix((TRANSPARENT), hover_bg, self.hover));
                    let x_color = mix((SLATE_400), (SLATE_400), self.dark_mode);
                    sdf.move_to(c.x - 3.0, c.y - 3.0);
                    sdf.line_to(c.x + 3.0, c.y + 3.0);
                    sdf.stroke(x_color, 1.5);
                    sdf.move_to(c.x + 3.0, c.y - 3.0);
                    sdf.line_to(c.x - 3.0, c.y + 3.0);
                    sdf.stroke(x_color, 1.5);
                    return sdf.result;
                }
            }
        }
    }

    // Home tab widget - no close button
    pub HomeTabWidget = <View> {
        width: Fit, height: 36
        flow: Right
        align: {y: 0.5}
        padding: {left: 12, right: 12, top: 0, bottom: 0}
        cursor: Hand
        show_bg: true
        draw_bg: {
            instance active: 0.0
            instance dark_mode: 0.0
            fn pixel(self) -> vec4 {
                let sdf = Sdf2d::viewport(self.pos * self.rect_size);
                sdf.box(0., 0., self.rect_size.x, self.rect_size.y + 4.0, 6.0);
                let light_inactive = (SLATE_200);
                let light_active = (WHITE);
                let dark_inactive = (SLATE_700);
                let dark_active = (SLATE_800);
                let inactive = mix(light_inactive, dark_inactive, self.dark_mode);
                let active_color = mix(light_active, dark_active, self.dark_mode);
                let color = mix(inactive, active_color, self.active);
                sdf.fill(color);
                return sdf.result;
            }
        }

        <Icon> {
            margin: {right: 6}
            draw_icon: {
                svg_file: dep("crate://self/resources/icons/app.svg")
                fn get_color(self) -> vec4 { return (ACCENT_BLUE); }
            }
            icon_walk: {width: 14, height: 14}
        }

        tab_label = <Label> {
            text: "MoFA FM"
            draw_text: {
                instance active: 0.0
                instance dark_mode: 0.0
                text_style: <FONT_MEDIUM>{ font_size: 11.0 }
                fn get_color(self) -> vec4 {
                    let light_inactive = (SLATE_500);
                    let light_active = (SLATE_800);
                    let dark_inactive = (SLATE_400);
                    let dark_active = (SLATE_200);
                    let inactive = mix(light_inactive, dark_inactive, self.dark_mode);
                    let active_color = mix(light_active, dark_active, self.dark_mode);
                    return mix(inactive, active_color, self.active);
                }
            }
        }
    }

    // Tab bar container
    pub TabBar = <View> {
        width: Fill, height: 36
        flow: Right
        spacing: 2
        padding: {left: 12, top: 0}
        show_bg: true
        draw_bg: {
            instance dark_mode: 0.0
            fn pixel(self) -> vec4 {
                return mix((SLATE_200), (SLATE_700), self.dark_mode);
            }
        }
    }
}
