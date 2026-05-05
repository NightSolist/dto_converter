// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesCPUThread {
    pub id: i64,

    pub numanode: u64,

    pub thread: u64,

    pub online: bool,

    pub isolated: bool,

}