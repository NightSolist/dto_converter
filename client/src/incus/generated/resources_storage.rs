// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesStorageDisk;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesStorage {
    pub disks: Vec<ResourcesStorageDisk>,

    pub total: u64,

}