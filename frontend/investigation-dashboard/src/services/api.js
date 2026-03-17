import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE !== undefined ? process.env.REACT_APP_API_BASE : 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const login = (username, password) =>
  api.post('/api/auth/login', { username, password });

// Alerts
export const getAlerts = (params) => api.get('/api/alerts', { params });
export const getAlert = (id) => api.get(`/api/alerts/${id}`);
export const updateAlert = (id, data) => api.put(`/api/alerts/${id}`, data);
export const assignAlert = (id, analyst) =>
  api.post(`/api/alerts/${id}/assign`, { analyst_id: analyst });
export const escalateAlert = (id, reason) =>
  api.post(`/api/alerts/${id}/escalate`, { reason });
export const closeAlert = (id, reason) =>
  api.post(`/api/alerts/${id}/close`, { resolution: reason });

// Cases
export const getCases = (params) => api.get('/api/cases', { params });
export const getCase = (id) => api.get(`/api/cases/${id}`);
export const createCase = (data) => api.post('/api/cases', data);
export const updateCase = (id, data) => api.put(`/api/cases/${id}`, data);
export const escalateCase = (id, data) => api.post(`/api/cases/${id}/escalate`, data);
export const closeCase = (id, data) => api.post(`/api/cases/${id}/close`, data);
export const getCaseNotes = (id) => api.get(`/api/cases/${id}/notes`);
export const addCaseNote = (id, data) => api.post(`/api/cases/${id}/notes`, data);
export const generateSAR = (id) => api.post(`/api/cases/${id}/generate-sar`);

// Sanctions Screening
export const screenEntity = (data) => api.post('/api/sanctions/screen', data);
export const batchScreen = (data) => api.post('/api/sanctions/batch-screen', data);

// Customer Risk
export const getCustomerRisk = (customerId) =>
  api.get(`/api/risk/customer/${customerId}`);
export const batchRiskScore = (data) => api.post('/api/risk/batch-score', data);

// Network Analytics
export const detectFraudRings = () => api.get('/api/network/fraud-rings');
export const getCustomerNetwork = (customerId) =>
  api.get(`/api/network/customer/${customerId}`);
export const getSharedDevices = () => api.get('/api/network/shared-devices');
export const getCircularTransfers = () => api.get('/api/network/circular-transfers');

// Regulatory Reporting
export const getSARReports = (params) => api.get('/api/reports/sar', { params });
export const getCTRReports = (params) => api.get('/api/reports/ctr', { params });
export const submitSAR = (id) => api.post(`/api/reports/sar/${id}/submit`);
export const approveSAR = (id) => api.post(`/api/reports/sar/${id}/approve`);
export const fileSAR = (id) => api.post(`/api/reports/sar/${id}/file`);

// AI/ML Scoring
export const getCompositeScore = (data) => api.post('/api/ml/composite-score', data);
export const getModelRegistry = () => api.get('/api/ml/models');

// Audit Logs
export const getAuditLogs = (params) => api.get('/api/audit/logs', { params });
export const getUserAudit = (userId) => api.get(`/api/audit/user/${userId}`);

// Service Status
export const getServiceStatus = () => api.get('/api/services/status');

// Data Sources
export const getDataSources = () => api.get('/api/admin/data-sources');
export const testDataSourceConnection = (sourceId) =>
  api.post(`/api/admin/data-sources/${sourceId}/test`);
export const getConnectionDetails = (sourceId) =>
  api.get(`/api/admin/data-sources/${sourceId}/connection-details`);
export const verifyAllConnections = () =>
  api.post('/api/admin/data-sources/verify-all');
export const getFieldMappings = () =>
  api.get('/api/admin/data-sources/field-mappings');
export const runTestIngestion = () =>
  api.post('/api/admin/data-sources/test-ingestion');
export const verifyExternalFeeds = () =>
  api.get('/api/admin/data-sources/external-feeds');
export const runTestPipeline = () =>
  api.post('/api/admin/data-sources/test-pipeline');
export const getDataSourceMetrics = () =>
  api.get('/api/admin/data-sources/metrics');
export const getDataSourceInventory = () =>
  api.get('/api/admin/data-sources/inventory');
export const verifyCapabilities = () =>
  api.post('/api/admin/data-sources/verify-capabilities');

// CDD/EDD
export const verifyCDDCapabilities = () =>
  api.post('/api/admin/data-sources/verify-capabilities');
export const getCustomerProfiles = () =>
  api.get('/api/admin/data-sources/cdd-edd/profiles');
export const checkOverdueReviews = () =>
  api.post('/api/admin/data-sources/cdd-edd/kyc-refresh/check');
export const getEddWorkflows = (status) =>
  api.get('/api/admin/data-sources/cdd-edd/edd/workflows', { params: status ? { status } : {} });
export const screenPEP = (name) =>
  api.post('/api/admin/data-sources/cdd-edd/screen/pep', { name, include_rca: true });
export const screenAdverseMedia = (name) =>
  api.post('/api/admin/data-sources/cdd-edd/screen/adverse-media', { name });

// WLF
export const wlfScreenPayment = (data) =>
  api.post('/api/admin/data-sources/wlf/screen-payment', data);
export const wlfScreenBatch = (data) =>
  api.post('/api/admin/data-sources/wlf/screen-batch', data);
export const wlfScreenName = (name) =>
  api.post('/api/admin/data-sources/wlf/screen-name', { name });
export const getWlfAlerts = (params) =>
  api.get('/api/admin/data-sources/wlf/alerts', { params });
export const getWlfAlertGroups = () =>
  api.get('/api/admin/data-sources/wlf/alerts/groups');
export const getWlfAlertStats = () =>
  api.get('/api/admin/data-sources/wlf/alerts/stats');

// EFM (Enterprise Fraud Management)
export const efmAtoSimulate = (data) =>
  api.post('/api/admin/data-sources/efm/ato/simulate', data);
export const efmMuleSimulate = (data) =>
  api.post('/api/admin/data-sources/efm/mule/simulate', data);
export const efmCardSimulate = (data) =>
  api.post('/api/admin/data-sources/efm/card/simulate', data);
export const efmDeviceSimulate = (data) =>
  api.post('/api/admin/data-sources/efm/device/simulate', data);
export const efmBiometricsSimulate = (data) =>
  api.post('/api/admin/data-sources/efm/biometrics/simulate', data);
export const efmPaymentSimulate = (data) =>
  api.post('/api/admin/data-sources/efm/payment/simulate', data);
export const efmCrossChannelSimulate = (data) =>
  api.post('/api/admin/data-sources/efm/cross-channel/simulate', data);
export const getEfmInfo = () =>
  api.get('/api/admin/data-sources/efm/info');

// DBF (Digital Banking Fraud)
export const dbfLoginAnomalySimulate = (data) =>
  api.post('/api/admin/data-sources/dbf/login-anomaly/simulate', data);
export const dbfSessionHijackSimulate = (data) =>
  api.post('/api/admin/data-sources/dbf/session-hijack/simulate', data);
export const dbfBotSimulate = (data) =>
  api.post('/api/admin/data-sources/dbf/bot/simulate', data);
export const dbfSocialEngineeringSimulate = (data) =>
  api.post('/api/admin/data-sources/dbf/social-engineering/simulate', data);
export const getDbfInfo = () =>
  api.get('/api/admin/data-sources/dbf/info');

// PMF (Payments Fraud)
export const pmfAchSimulate = (data) =>
  api.post('/api/admin/data-sources/pmf/ach/simulate', data);
export const pmfWireSimulate = (data) =>
  api.post('/api/admin/data-sources/pmf/wire/simulate', data);
export const pmfRtpZelleSimulate = (data) =>
  api.post('/api/admin/data-sources/pmf/rtp-zelle/simulate', data);
export const pmfCnpSimulate = (data) =>
  api.post('/api/admin/data-sources/pmf/cnp/simulate', data);
export const pmfCheckSimulate = (data) =>
  api.post('/api/admin/data-sources/pmf/check/simulate', data);
export const getPmfInfo = () =>
  api.get('/api/admin/data-sources/pmf/info');

// KYC / CDD Lifecycle Management
export const getKycDashboard = () =>
  api.get('/api/admin/data-sources/kyc/dashboard');
export const getKycCases = () =>
  api.get('/api/admin/data-sources/kyc/cases');
export const kycOnboard = (data) =>
  api.post('/api/admin/data-sources/kyc/onboard', data);
export const kycPeriodicReviewCheck = () =>
  api.post('/api/admin/data-sources/kyc/periodic-review/check');
export const kycTriggerEvent = (data) =>
  api.post('/api/admin/data-sources/kyc/trigger-event', data);
export const getKycTriggerEvents = () =>
  api.get('/api/admin/data-sources/kyc/trigger-events');
export const kycIntegrate = (system, customerId) =>
  api.post(`/api/admin/data-sources/kyc/integrate/${system}/${customerId}`);
export const getKycStatusMachine = () =>
  api.get('/api/admin/data-sources/kyc/status-machine');
export const getKycInfo = () =>
  api.get('/api/admin/data-sources/kyc/info');

// ActOne Case Management (Investigation Hub)
export const getActoneDashboard = () =>
  api.get('/api/admin/data-sources/actone/dashboard');
export const getActoneCases = () =>
  api.get('/api/admin/data-sources/actone/cases');
export const actoneTriage = (data) =>
  api.post('/api/admin/data-sources/actone/triage', data);
export const actoneScenarioAml = () =>
  api.post('/api/admin/data-sources/actone/scenarios/aml-investigation');
export const actoneScenarioFraud = () =>
  api.post('/api/admin/data-sources/actone/scenarios/fraud-case');
export const actoneScenarioSurveillance = () =>
  api.post('/api/admin/data-sources/actone/scenarios/surveillance');
export const getActoneCustomer360 = (customerId) =>
  api.get(`/api/admin/data-sources/actone/customer360/${customerId}`);
export const getActoneStateMachine = () =>
  api.get('/api/admin/data-sources/actone/state-machine');
export const getActoneAudit = () =>
  api.get('/api/admin/data-sources/actone/audit');
export const getActoneInfo = () =>
  api.get('/api/admin/data-sources/actone/info');

// ═══════════════════ AI/ML Analytics & Risk Scoring ═══════════════════
export const getAimlDashboard = () =>
  api.get('/api/admin/data-sources/aiml/dashboard');
export const getAimlModels = () =>
  api.get('/api/admin/data-sources/aiml/models');
export const aimlPredictAml = (data) =>
  api.post('/api/admin/data-sources/aiml/predict/aml', data);
export const aimlPredictFraud = (data) =>
  api.post('/api/admin/data-sources/aiml/predict/fraud', data);
export const aimlBehavioralUpdate = (data) =>
  api.post('/api/admin/data-sources/aiml/behavioral/update', data);
export const aimlPeerGroupAnalyze = (data) =>
  api.post('/api/admin/data-sources/aiml/peer-group/analyze', data);
export const aimlAnomalyDetect = (data) =>
  api.post('/api/admin/data-sources/aiml/anomaly/detect', data);
export const aimlRiskPredict = (data) =>
  api.post('/api/admin/data-sources/aiml/risk/predict', data);
export const aimlXaiExplain = (data) =>
  api.post('/api/admin/data-sources/aiml/xai/explain', data);
export const getAimlGovernance = () =>
  api.get('/api/admin/data-sources/aiml/governance');
export const aimlIngestionRun = (data) =>
  api.post('/api/admin/data-sources/aiml/ingestion/run', data);
export const aimlSimulationRun = (data) =>
  api.post('/api/admin/data-sources/aiml/simulation/run', data);
export const aimlScenarioAlertReduction = () =>
  api.post('/api/admin/data-sources/aiml/scenarios/alert-reduction');
export const aimlScenarioPredictiveFraud = () =>
  api.post('/api/admin/data-sources/aiml/scenarios/predictive-fraud');
export const aimlScenarioRiskUpdate = () =>
  api.post('/api/admin/data-sources/aiml/scenarios/risk-score-update');
export const getAimlInfo = () =>
  api.get('/api/admin/data-sources/aiml/info');

export default api;
