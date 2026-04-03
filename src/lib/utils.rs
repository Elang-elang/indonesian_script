use super::variable::Value;
pub fn extract_int(v: Value) -> i64 {
    match v {
        Value::Angka(n) => n,
        _ => 0,
    }
}
