// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesGPUCard;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesGPUCardSRIOV {
    pub currentvfs: u64,

    pub maximumvfs: u64,

    pub vfs: Vec<ResourcesGPUCard>,

}