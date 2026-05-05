// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use serde_json;
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Event {
    #[serde(rename = "type")]    pub r#type: String,

    pub timestamp: chrono::DateTime<chrono::Utc>,

    pub metadata: serde_json::Value,

    #[serde(skip_serializing_if = "Option::is_none")]    pub location: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub project: Option<String>,

}