// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ClusterMemberSysInfo {
    pub uptime: i64,

    pub loadaverages: Vec<f64>,

    pub totalram: u64,

    pub freeram: u64,

    pub sharedram: u64,

    pub bufferram: u64,

    pub totalswap: u64,

    pub freeswap: u64,

    pub processes: u16,

}