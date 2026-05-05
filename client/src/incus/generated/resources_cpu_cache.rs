// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesCPUCache {
    pub level: u64,

    #[serde(rename = "type")]    pub r#type: String,

    pub size: u64,

}