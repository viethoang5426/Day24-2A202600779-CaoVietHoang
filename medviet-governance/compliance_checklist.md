# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [x] Tất cả patient data lưu trên servers đặt tại Việt Nam
- [x] Backup cũng phải ở trong lãnh thổ VN
- [x] Log việc transfer data ra ngoài nếu có

## B. Explicit Consent
- [x] Thu thập consent trước khi dùng data cho AI training
- [x] Có mechanism để user rút consent (Right to Erasure) — DELETE /api/patients/{id}
- [x] Lưu consent record với timestamp

## C. Breach Notification (72h)
- [x] Có incident response plan
- [x] Alert tự động khi phát hiện breach
- [x] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h

## D. DPO Appointment
- [x] Đã bổ nhiệm Data Protection Officer
- [x] DPO có thể liên hệ tại: dpo@medviet.vn — Nguyễn Văn An, Data Protection Officer

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) — detect CCCD, SĐT, email, tên với detection rate ≥95% | ✅ Done | AI Team |
| Access control | RBAC (Casbin) 4 roles + ABAC (OPA) + FastAPI middleware kiểm tra Bearer token | ✅ Done | Platform Team |
| Encryption | AES-256-GCM envelope encryption (KEK→DEK→Data), key rotation hỗ trợ | ✅ Done | Infra Team |
| Audit logging | Structured logging với Python logging module, ghi lại mọi API request (user, resource, action, timestamp). Tích hợp ELK Stack (Elasticsearch + Logstash + Kibana) cho centralized log management. API access logs lưu trữ tối thiểu 3 năm theo NĐ13. | ✅ Done | Platform Team |
| Breach detection | Prometheus + Grafana monitoring stack (docker-compose.yml). Alert rules cho: (1) bất thường số lượng API calls, (2) failed authentication attempts > threshold, (3) unauthorized access attempts (403 responses). Tích hợp PagerDuty/Slack webhook để notify security team trong < 15 phút. | ✅ Done | Security Team |

## F. Các biện pháp bổ sung

### Audit Logging — Chi tiết triển khai
- **Công nghệ**: Python `logging` module + ELK Stack
- **Format**: JSON structured logs với fields: timestamp, user_id, role, resource, action, result (allow/deny), IP address
- **Retention**: Logs lưu trữ tối thiểu 3 năm trên storage servers tại Việt Nam
- **Immutability**: Append-only log files, không cho phép sửa đổi/xóa
- **API middleware**: FastAPI middleware ghi log mọi request/response

### Breach Detection — Chi tiết triển khai
- **Monitoring**: Prometheus thu thập metrics từ FastAPI (request count, latency, error rate)
- **Visualization**: Grafana dashboards hiển thị real-time traffic patterns
- **Alert rules**:
  - Failed auth > 10 lần/phút → cảnh báo brute-force
  - 403 responses > 20 lần/phút → cảnh báo unauthorized access
  - Bất thường data export volume → cảnh báo data exfiltration
- **Incident Response**: Tự động block IP sau 5 failed attempts, notify DPO qua email trong 15 phút
- **Compliance**: Báo cáo breach đến Bộ Công an trong 72h theo quy định NĐ13/2023
