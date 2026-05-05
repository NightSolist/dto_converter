use serde::{Serialize, Deserialize};
use crate::incus::ConfigMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StoragePoolPut {
    pub config: ConfigMap,
    pub description: String,
}