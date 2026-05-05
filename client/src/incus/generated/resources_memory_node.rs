// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesMemoryNode {
    pub numanode: u64,

    pub hugepagesused: u64,

    pub hugepagestotal: u64,

    pub used: u64,

    pub total: u64,

}