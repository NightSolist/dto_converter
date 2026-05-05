// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ImageMetadataTemplate {
    pub when: Vec<String>,

    pub createonly: bool,

    pub template: String,

    pub properties: HashMap<String, String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub uid: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub gid: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub mode: Option<String>,

}