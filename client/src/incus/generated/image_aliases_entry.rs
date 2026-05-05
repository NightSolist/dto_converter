// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ImageAliasesEntry {
    pub name: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub description: String,

    pub target: String,

}