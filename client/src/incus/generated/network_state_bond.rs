// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkStateBond {
    pub mode: String,

    pub transmitpolicy: String,

    pub updelay: u64,

    pub downdelay: u64,

    pub miifrequency: u64,

    pub miistate: String,

    pub lowerdevices: Vec<String>,

}