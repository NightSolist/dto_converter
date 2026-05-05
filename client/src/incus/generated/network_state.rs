// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::NetworkStateAddress;
use crate::incus::NetworkStateBond;
use crate::incus::NetworkStateBridge;
use crate::incus::NetworkStateCounters;
use crate::incus::NetworkStateOVN;
use crate::incus::NetworkStateVLAN;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkState {
    pub addresses: Vec<NetworkStateAddress>,

    pub counters: Option<NetworkStateCounters>,

    pub hwaddr: String,

    pub mtu: i64,

    pub state: String,

    #[serde(rename = "type")]    pub r#type: String,

    pub bond: Option<NetworkStateBond>,

    pub bridge: Option<NetworkStateBridge>,

    pub vlan: Option<NetworkStateVLAN>,

    pub ovn: Option<NetworkStateOVN>,

}