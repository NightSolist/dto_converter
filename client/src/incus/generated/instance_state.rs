// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;use crate::incus::InstanceStateCPU;
use crate::incus::InstanceStateDisk;
use crate::incus::InstanceStateMemory;
use crate::incus::InstanceStateNetwork;
use crate::incus::InstanceStateOSInfo;
use crate::incus::StatusCode;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstanceState {
    pub status: String,

    pub statuscode: StatusCode,

    pub disk: HashMap<String, InstanceStateDisk>,

    pub memory: InstanceStateMemory,

    pub network: HashMap<String, InstanceStateNetwork>,

    pub pid: i64,

    pub processes: i64,

    pub cpu: InstanceStateCPU,

    pub startedat: chrono::DateTime<chrono::Utc>,

    pub osinfo: Option<InstanceStateOSInfo>,

}