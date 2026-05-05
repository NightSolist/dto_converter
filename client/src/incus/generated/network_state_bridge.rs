// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkStateBridge {
    pub id: String,

    pub stp: bool,

    pub forwarddelay: u64,

    pub vlandefault: u64,

    pub vlanfiltering: bool,

    pub upperdevices: Vec<String>,

}