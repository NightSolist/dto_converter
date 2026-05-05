// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesPCIDevice;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesPCI {
    pub devices: Vec<ResourcesPCIDevice>,

    pub total: u64,

}