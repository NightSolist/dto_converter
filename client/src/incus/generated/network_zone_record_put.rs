// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;
use crate::incus::NetworkZoneRecordEntry;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkZoneRecordPut {
    pub description: String,

    pub entries: Vec<NetworkZoneRecordEntry>,

    pub config: ConfigMap,

}