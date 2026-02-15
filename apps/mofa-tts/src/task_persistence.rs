//! Task persistence module for saving/loading clone tasks
//!
//! Clone tasks are stored in:
//! - Config: ~/.dora/primespeech/clone_tasks.json
//! - Audio: ~/.dora/primespeech/clone_tasks/{task_id}/

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

/// Clone task status
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub enum CloneTaskStatus {
    Pending,
    Processing,
    Completed,
    Failed,
    Cancelled,
}

/// Clone task information
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CloneTask {
    pub id: String,
    pub name: String,
    pub status: CloneTaskStatus,
    pub progress: f32,
    pub created_at: String,
    pub audio_path: Option<String>,
    pub reference_text: Option<String>,
    pub started_at: Option<String>,
    pub completed_at: Option<String>,
    pub message: Option<String>,
}

/// Clone tasks configuration file format
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CloneTasksConfig {
    /// Config version for future compatibility
    pub version: String,
    /// List of clone tasks
    pub tasks: Vec<CloneTask>,
}

impl Default for CloneTasksConfig {
    fn default() -> Self {
        Self {
            version: "1.0".to_string(),
            tasks: Vec::new(),
        }
    }
}

/// Get the base directory for PrimeSpeech data
pub fn get_primespeech_dir() -> PathBuf {
    let home = dirs::home_dir().unwrap_or_else(|| PathBuf::from("."));
    home.join(".dora").join("primespeech")
}

/// Get the clone tasks config file path
pub fn get_config_path() -> PathBuf {
    get_primespeech_dir().join("clone_tasks.json")
}

/// Get the clone tasks directory
pub fn get_clone_tasks_dir() -> PathBuf {
    get_primespeech_dir().join("clone_tasks")
}

/// Get the directory for a specific clone task
pub fn get_task_dir(task_id: &str) -> PathBuf {
    get_clone_tasks_dir().join(task_id)
}

/// Ensure all required directories exist
pub fn ensure_directories() -> std::io::Result<()> {
    let primespeech_dir = get_primespeech_dir();
    if !primespeech_dir.exists() {
        fs::create_dir_all(&primespeech_dir)?;
    }

    let clone_tasks_dir = get_clone_tasks_dir();
    if !clone_tasks_dir.exists() {
        fs::create_dir_all(&clone_tasks_dir)?;
    }

    Ok(())
}

/// Load clone tasks from config file
pub fn load_clone_tasks() -> Vec<CloneTask> {
    let config_path = get_config_path();

    if !config_path.exists() {
        return Vec::new();
    }

    match fs::read_to_string(&config_path) {
        Ok(content) => match serde_json::from_str::<CloneTasksConfig>(&content) {
            Ok(config) => config.tasks,
            Err(e) => {
                log::error!("Failed to parse clone tasks config: {}", e);
                Vec::new()
            }
        },
        Err(e) => {
            log::error!("Failed to read clone tasks config: {}", e);
            Vec::new()
        }
    }
}

/// Save clone tasks to config file
pub fn save_clone_tasks(tasks: &[CloneTask]) -> Result<(), String> {
    ensure_directories().map_err(|e| format!("Failed to create directories: {}", e))?;

    let config = CloneTasksConfig {
        version: "1.0".to_string(),
        tasks: tasks.to_vec(),
    };

    let config_path = get_config_path();
    let json = serde_json::to_string_pretty(&config)
        .map_err(|e| format!("Failed to serialize config: {}", e))?;

    fs::write(&config_path, json).map_err(|e| format!("Failed to write config: {}", e))?;

    log::info!("Saved {} clone tasks to {:?}", tasks.len(), config_path);
    Ok(())
}

/// Add a new clone task
pub fn add_task(task: CloneTask) -> Result<(), String> {
    let mut tasks = load_clone_tasks();
    tasks.push(task);
    save_clone_tasks(&tasks)
}

/// Update an existing clone task
pub fn update_task(task: CloneTask) -> Result<(), String> {
    let mut tasks = load_clone_tasks();
    
    if let Some(existing) = tasks.iter_mut().find(|t| t.id == task.id) {
        *existing = task;
        save_clone_tasks(&tasks)
    } else {
        Err(format!("Task not found: {}", task.id))
    }
}

/// Delete a clone task
pub fn delete_task(task_id: &str) -> Result<(), String> {
    let mut tasks = load_clone_tasks();
    tasks.retain(|t| t.id != task_id);
    save_clone_tasks(&tasks)?;

    // Also delete the task directory if it exists
    let task_dir = get_task_dir(task_id);
    if task_dir.exists() {
        fs::remove_dir_all(&task_dir)
            .map_err(|e| format!("Failed to delete task directory: {}", e))?;
    }

    Ok(())
}

/// Get a specific task by ID
pub fn get_task(task_id: &str) -> Option<CloneTask> {
    load_clone_tasks().into_iter().find(|t| t.id == task_id)
}
