import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
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
    });

    if (!response.data) {
      throw new Error('No data received from server');
    }

    const audioBlob = new Blob([response.data], { type: 'audio/wav' });
    return URL.createObjectURL(audioBlob);
  } catch (error) {
    console.error('Error enhancing audio:', error);
    throw error;
  }
}

export async function reduceNoise(file: File): Promise<string> {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post('/reduce-noise', formData, {
      responseType: 'blob',
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (!response.data) {
      throw new Error('No data received from server');
    }

    const audioBlob = new Blob([response.data], { type: 'audio/wav' });
    return URL.createObjectURL(audioBlob);
  } catch (error) {
    console.error('Error reducing noise:', error);
    throw error;
  }
}

export async function createHighlights(file: File): Promise<string> {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post('/create-highlights', formData, {
      responseType: 'blob',
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (!response.data) {
      throw new Error('No data received from server');
    }

    const videoBlob = new Blob([response.data], { type: 'video/mp4' });
    return URL.createObjectURL(videoBlob);
  } catch (error) {
    console.error('Error creating highlights:', error);
    throw error;
  }
}

export const editVideo = (formData: FormData) => {
  return api.post('/edit-video', formData, {
    responseType: 'blob',
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};