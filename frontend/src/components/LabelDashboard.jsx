import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Database, FileText, Printer, AlertCircle, CheckCircle, RefreshCw } from 'lucide-react';

const LabelDashboard = ({
    apiBaseUrl,
    onStatusChange,
    isLoading,
    setIsLoading,
    selectedPrinter,
    labelSettings
}) => {
    const [systems, setSystems] = useState([]);
    const [formData, setFormData] = useState({
        system: '',
        year: new Date().getFullYear().toString(),
        month: (new Date().getMonth() + 1).toString().padStart(2, '0'),
        startSerial: '',
        quantity: 1
    });
    const [previewData, setPreviewData] = useState(null);
    const [duplicatesInfo, setDuplicatesInfo] = useState({ hasCheck: false, list: [] });

    useEffect(() => {
        // Helper to pad month
        const now = new Date();
        const currentMonth = (now.getMonth() + 1).toString().padStart(2, '0');
        setFormData(prev => ({ ...prev, month: currentMonth }));

        const fetchSystems = async () => {
            try {
                const response = await axios.get(`${apiBaseUrl}/api/systems`);
                setSystems(response.data);
                if (response.data.length > 0) {
                    setFormData(prev => ({ ...prev, system: response.data[0] }));
                }
            } catch (error) {
                onStatusChange({ type: 'error', message: 'Failed to fetch systems' });
            }
        };
        fetchSystems();
    }, [apiBaseUrl]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        // Reset duplicate check if inputs change
        setDuplicatesInfo({ hasCheck: false, list: [] });
    };

    const checkDuplicates = async () => {
        if (!formData.startSerial || !formData.system) {
            onStatusChange({ type: 'error', message: 'Please select system and enter serial' });
            return;
        }

        setIsLoading(true);
        onStatusChange({ type: 'loading', message: 'Checking for duplicate serial numbers...' });

        try {
            const response = await axios.post(`${apiBaseUrl}/api/check-duplicates`, {
                system_name: formData.system,
                year: formData.year,
                month: formData.month,
                start_serial: formData.startSerial,
                quantity: formData.quantity
            });

            if (response.data.success) {
                setDuplicatesInfo({
                    hasCheck: true,
                    list: response.data.duplicates
                });
                if (response.data.has_duplicates) {
                    onStatusChange({
                        type: 'error',
                        message: `Found ${response.data.duplicates.length} duplicate(s)`
                    });
                } else {
                    onStatusChange({ type: 'idle', message: 'No duplicates found. Ready to generate.' });
                }
            }
        } catch (error) {
            onStatusChange({ type: 'error', message: 'Duplicate check failed' });
        } finally {
            setIsLoading(false);
        }
    };

    const generateBatch = async () => {
        setIsLoading(true);
        onStatusChange({ type: 'loading', message: 'Generating label batch...' });

        try {
            const response = await axios.post(`${apiBaseUrl}/api/generate-batch`, {
                system_name: formData.system,
                year: formData.year,
                month: formData.month,
                start_serial: formData.startSerial,
                quantity: formData.quantity,
                label_settings: labelSettings
            });

            if (response.data.success) {
                setPreviewData(response.data);
                onStatusChange({ type: 'idle', message: 'Batch generated successfully' });
            } else {
                onStatusChange({ type: 'error', message: response.data.error });
            }
        } catch (error) {
            onStatusChange({ type: 'error', message: error.response?.data?.error || 'Generation failed' });
        } finally {
            setIsLoading(false);
        }
    };

    const printBatch = async () => {
        if (!previewData || !previewData.pdf_url) return;

        setIsLoading(true);
        onStatusChange({ type: 'loading', message: 'Sending to printer...' });

        try {
            const response = await axios.post(`${apiBaseUrl}/api/print-label`, {
                pdf_url: previewData.pdf_url,
                printer_name: selectedPrinter
            });

            if (response.data.success) {
                onStatusChange({ type: 'success', message: 'Batch sent to printer successfully' });
            } else {
                onStatusChange({ type: 'error', message: response.data.error });
            }
        } catch (error) {
            onStatusChange({ type: 'error', message: 'Printing failed' });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="dashboard-layout">
            <div className="left-panel">
                <div className="configuration-card">
                    <div className="card-header">
                        <FileText size={20} />
                        <h2>Batch Configuration</h2>
                    </div>

                    <div className="form-grid">
                        <div className="form-group">
                            <label>Select System</label>
                            <select name="system" value={formData.system} onChange={handleInputChange}>
                                {systems.map(s => <option key={s} value={s}>{s}</option>)}
                            </select>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Year</label>
                                <input type="text" value={formData.year} readOnly className="read-only" />
                            </div>
                            <div className="form-group">
                                <label>Month</label>
                                <input type="text" value={formData.month} readOnly className="read-only" />
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Starting Serial Number</label>
                            <input
                                type="text"
                                name="startSerial"
                                value={formData.startSerial}
                                onChange={handleInputChange}
                                placeholder="e.g. 0001"
                            />
                        </div>

                        <div className="form-group">
                            <label>Quantity</label>
                            <input
                                type="number"
                                name="quantity"
                                value={formData.quantity}
                                onChange={handleInputChange}
                                min="1"
                                max="500"
                            />
                        </div>
                    </div>

                    <div className="action-buttons">
                        <button
                            className="secondary-btn"
                            onClick={checkDuplicates}
                            disabled={isLoading || !formData.startSerial}
                        >
                            <Database size={16} /> Check Duplicates
                        </button>
                        <button
                            className="primary-btn"
                            onClick={generateBatch}
                            disabled={isLoading || !formData.startSerial || (duplicatesInfo.hasCheck && duplicatesInfo.list.length > 0)}
                        >
                            {isLoading ? <RefreshCw className="spinning" size={16} /> : <FileText size={16} />}
                            Generate Labels
                        </button>
                    </div>

                    {duplicatesInfo.hasCheck && (
                        <div className={`duplicate-status ${duplicatesInfo.list.length > 0 ? 'error' : 'success'}`}>
                            {duplicatesInfo.list.length > 0 ? (
                                <>
                                    <AlertCircle size={16} />
                                    <span>Found duplicates: {duplicatesInfo.list.join(', ')}</span>
                                </>
                            ) : (
                                <>
                                    <CheckCircle size={16} />
                                    <span>All serial numbers are available!</span>
                                </>
                            )}
                        </div>
                    )}
                </div>

                <div className="instructions">
                    <h3>Brady System Instructions</h3>
                    <ul>
                        <li>Select the target system from the dropdown.</li>
                        <li>Enter the <strong>starting</strong> serial number. Leading zeros will be preserved.</li>
                        <li>Specify how many labels you need (batch generation).</li>
                        <li>Click "Check Duplicates" to verify serial numbers are available.</li>
                        <li>Click "Generate" to create and preview the combined PDF.</li>
                    </ul>
                </div>
            </div>

            <div className="right-panel">
                <div className="preview-panel">
                    <div className="preview-header">
                        <h3>Label Preview</h3>
                        <button
                            className="print-btn"
                            disabled={!previewData || isLoading}
                            onClick={printBatch}
                        >
                            <Printer size={16} /> Print Batch
                        </button>
                    </div>

                    <div className="preview-container">
                        {previewData ? (
                            <iframe
                                src={`${apiBaseUrl}${previewData.pdf_url}#toolbar=0&navpanes=0`}
                                className="preview-frame"
                                title="Batch Preview"
                            />
                        ) : (
                            <div className="preview-placeholder">
                                <FileText size={48} className="placeholder-icon" />
                                <p>Configure and generate to see preview</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LabelDashboard;
