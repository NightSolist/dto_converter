// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesUSBDevice;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesUSB {
    pub devices: Vec<ResourcesUSBDevice>,

    pub total: u64,

}