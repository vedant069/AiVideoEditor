import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 300000, // 5 minutes timeout since audio processing takes time
});

export async function enhanceAudio(file: File): Promise<string> {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post('/enhance-audio', formData, {
      responseType: 'blob',
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        console.log('Upload Progress:', progressEvent.loaded / progressEvent.total * 100, '%');
      },
    });

    if (!response.data) {
      throw new Error('No data received from server');
    }

    // Verify that we received an audio file
    const contentType = response.headers['content-type'];
    if (!contentType || !contentType.includes('audio/')) {
      throw new Error('Invalid response format: Expected audio file');
    }

    // Create a blob from the response data with the correct MIME type
    const audioBlob = new Blob([response.data], { type: contentType });
    return URL.createObjectURL(audioBlob);
  } catch (error) {
    console.error('Error enhancing audio:', error);
    throw error;
  }
}