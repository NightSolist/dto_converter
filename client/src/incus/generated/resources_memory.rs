// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesMemoryNode;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesMemory {
    #[serde(skip_serializing_if = "Option::is_none")]    pub nodes: Option<Vec<ResourcesMemoryNode>>,

    pub hugepagestotal: u64,

    pub hugepagesused: u64,

    pub hugepagessize: u64,

    pub used: u64,

    pub total: u64,

}