// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesStorageDiskPartition {
    pub id: String,

    pub device: String,

    pub readonly: bool,

    pub size: u64,

    pub partition: u64,

}