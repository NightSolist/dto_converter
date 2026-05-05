// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;use crate::incus::ClusterMemberSysInfo;
use crate::incus::StoragePoolState;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ClusterMemberState {
    pub sysinfo: ClusterMemberSysInfo,

    pub storagepools: HashMap<String, StoragePoolState>,

}