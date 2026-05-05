// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::InstanceStateNetworkAddress;
use crate::incus::InstanceStateNetworkCounters;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstanceStateNetwork {
    pub addresses: Vec<InstanceStateNetworkAddress>,

    pub counters: InstanceStateNetworkCounters,

    pub hwaddr: String,

    pub hostname: String,

    pub mtu: i64,

    pub state: String,

    #[serde(rename = "type")]    pub r#type: String,

}