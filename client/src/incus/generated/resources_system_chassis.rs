// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesSystemChassis {
    pub vendor: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub serial: String,

    pub version: String,

}