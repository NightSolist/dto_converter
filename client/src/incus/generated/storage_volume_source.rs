// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StorageVolumeSource {
    pub name: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub pool: String,

    pub certificate: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub mode: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub operation: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub websockets: Option<HashMap<String, String>>,

    pub volumeonly: bool,

    pub refresh: bool,

    pub refreshexcludeolder: bool,

    #[serde(skip_serializing_if = "Option::is_none")]    pub project: Option<String>,

    pub location: String,

}