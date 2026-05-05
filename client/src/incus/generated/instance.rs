// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;
use crate::incus::DevicesMap;
use crate::incus::StatusCode;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Instance {
    pub createdat: chrono::DateTime<chrono::Utc>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub expandedconfig: Option<ConfigMap>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub expandeddevices: Option<DevicesMap>,

    pub name: String,

    pub status: String,

    pub statuscode: StatusCode,

    pub lastusedat: chrono::DateTime<chrono::Utc>,

    pub location: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub project: String,

    pub architecture: String,

    pub config: ConfigMap,

    pub devices: DevicesMap,

    pub ephemeral: bool,

    pub profiles: Vec<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub restore: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]    pub diskonly: Option<bool>,

    pub stateful: bool,

    pub description: String,

}