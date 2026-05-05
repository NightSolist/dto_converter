// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct MetadataConfigKey {
    #[serde(skip_serializing_if = "Option::is_none")]    pub condition: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub scope: Option<String>,

    #[serde(rename = "type")]    pub r#type: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub default: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub liveupdate: Option<String>,

    pub description: String,

    pub longdescription: String,

}