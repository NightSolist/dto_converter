// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstanceConsolePost {
    pub width: i64,

    pub height: i64,

    #[serde(rename = "type")]    pub r#type: String,

    pub force: bool,

}