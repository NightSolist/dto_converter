use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;
use crate::incus::DevicesMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ProfilePut {
    config: ConfigMap,
    description: String,
    devices: DevicesMap,
}