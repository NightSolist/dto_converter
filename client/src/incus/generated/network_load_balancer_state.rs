// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;use crate::incus::NetworkLoadBalancerStateBackendHealth;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkLoadBalancerState {
    pub backendhealth: HashMap<String, NetworkLoadBalancerStateBackendHealth>,

}