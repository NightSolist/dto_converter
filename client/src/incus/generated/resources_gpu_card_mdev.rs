// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesGPUCardMdev {
    pub api: String,

    pub available: u64,

    #[serde(skip_serializing_if = "Option::is_none")]    pub name: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub description: Option<String>,

    pub devices: Vec<String>,

}