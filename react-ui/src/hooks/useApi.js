import { useState, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const callTool = useCallback(async (service, toolName, params = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/call-tool`, {
        service,
        tool_name: toolName,
        params
      });
      
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'An error occurred';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const checkConnection = useCallback(async (service) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/status/${service}`);
      return response.data.connected;
    } catch (err) {
      return false;
    }
  }, []);

  const getConnectionInfo = useCallback(async (service) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/connection-info/${service}`);
      return response.data;
    } catch (err) {
      return null;
    }
  }, []);

  return {
    callTool,
    checkConnection,
    getConnectionInfo,
    loading,
    error
  };
};