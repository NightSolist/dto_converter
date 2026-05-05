// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesSerialDevice;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesSerial {
    pub devices: Vec<ResourcesSerialDevice>,

    pub total: u64,

}