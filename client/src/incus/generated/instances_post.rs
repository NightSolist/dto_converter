// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;
use crate::incus::DevicesMap;
use crate::incus::InstanceSource;
use crate::incus::InstanceType;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstancesPost {
    pub name: String,

    pub source: InstanceSource,

    pub instancetype: String,

    #[serde(rename = "type")]    pub r#type: InstanceType,

    pub start: bool,

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