use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;
use crate::incus::DevicesMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ProfilePut {
    pub config: ConfigMap,
    pub description: String,
    pub devices: DevicesMap,
}