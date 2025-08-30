module.exports = {
  govhack: {
    input: {
      target: 'http://localhost:8000/api/schema/',
      client: 'axios',
    },
    output: {
      mode: 'tags-split',
      target: 'src/services/api.ts',
      schemas: 'src/types/api.ts',
      client: 'axios',
      httpClient: 'axios',
      prettier: true,
      tsconfig: 'tsconfig.json',
      override: {
        mutator: {
          path: 'src/services/axiosConfig.ts',
          name: 'customAxiosInstance',
        },
      },
    },
    hooks: {
      afterAllFilesWrite: 'prettier --write',
    },
  },
};