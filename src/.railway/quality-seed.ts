// Compatibility adapter: the requested JSON files remain the per-service contract.
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { bucket, defineRailway, project, service, volume } from 'railway/iac';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = (path: string) => JSON.parse(readFileSync(resolve(root, path), 'utf8'));

export default defineRailway((ctx) => {
  const inventory = read('services.json');
  const regions = read('regions.json');
  if (!['us-west2', 'us-east4-eqdc4a', 'europe-west4-drams3a', 'asia-southeast1-eqsg3a'].includes(regions.service)) throw new Error('Unsupported service region');
  if (!['sjc', 'iad', 'ams', 'sin'].includes(regions.bucket)) throw new Error('Unsupported bucket region');
  const resources: any[] = [bucket('Nodestore', { region: regions.bucket }), bucket('Filestore', { region: regions.bucket })];
  for (const [name, metadata] of Object.entries<any>(inventory)) {
    const config = read(`${name}/railway.json`);
    const env = read(`${name}/variables.json`);
    const data = metadata.volume ? volume(`${name}-volume`, { region: regions.service }) : undefined;
    if (data) resources.push(data);
    resources.push(service(name, {
      source: { type: 'github', repo: 'kayossouza/railway-sentry', branch: 'main', rootDirectory: '/runtime' },
      build: { builder: "DOCKERFILE", dockerfilePath: config.build.dockerfilePath },
      deploy: config.deploy,
      regions: { [regions.service]: 1 },
      env,
      ...(data ? { volumeMounts: { [metadata.volume]: data } } : {}),
    }));
  }
  return project(ctx.projectName ?? 'sentry', { resources });
});
