// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstanceSource {
    #[serde(rename = "type")]    pub r#type: String,

    pub certificate: String,

    #[serde(skip_serializing_if = "Option::is_none")]    pub alias: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub fingerprint: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub properties: Option<HashMap<String, String>>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub server: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub secret: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub protocol: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub baseimage: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub mode: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub operation: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub websockets: Option<HashMap<String, String>>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub source: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub live: Option<bool>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub instanceonly: Option<bool>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub refresh: Option<bool>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub refreshexcludeolder: Option<bool>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub project: Option<String>,

    pub allowinconsistent: bool,

}