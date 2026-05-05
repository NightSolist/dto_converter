// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;
use crate::incus::DevicesMap;
use crate::incus::InstancePostTarget;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstancePost {
    pub name: String,

    pub migration: bool,

    pub live: bool,

    pub instanceonly: bool,

    pub target: Option<InstancePostTarget>,

    pub pool: String,

    pub project: String,

    pub allowinconsistent: bool,

    pub config: ConfigMap,

    pub devices: DevicesMap,

    pub profiles: Vec<String>,

}