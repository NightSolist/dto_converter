use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;
use crate::incus::DevicesMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstancePut {
    architecture: String,
    config: ConfigMap,
    devices: DevicesMap,
    ephemeral: bool,
    profiles: Vec<String>,
    restore: Option<String>,
    disk_only: Option<bool>,
    stateful: Option<bool>,
    description: String,
}