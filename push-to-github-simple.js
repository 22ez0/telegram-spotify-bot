import { Octokit } from '@octokit/rest';
import { readFileSync, readdirSync, statSync } from 'fs';
import { join, relative } from 'path';

let connectionSettings;

async function getAccessToken() {
  if (connectionSettings && connectionSettings.settings.expires_at && new Date(connectionSettings.settings.expires_at).getTime() > Date.now()) {
    return connectionSettings.settings.access_token;
  }
  
  const hostname = process.env.REPLIT_CONNECTORS_HOSTNAME;
  const xReplitToken = process.env.REPL_IDENTITY 
    ? 'repl ' + process.env.REPL_IDENTITY 
    : process.env.WEB_REPL_RENEWAL 
    ? 'depl ' + process.env.WEB_REPL_RENEWAL 
    : null;

  if (!xReplitToken) {
    throw new Error('X_REPLIT_TOKEN not found for repl/depl');
  }

  connectionSettings = await fetch(
    'https://' + hostname + '/api/v2/connection?include_secrets=true&connector_names=github',
    {
      headers: {
        'Accept': 'application/json',
        'X_REPLIT_TOKEN': xReplitToken
      }
    }
  ).then(res => res.json()).then(data => data.items?.[0]);

  const accessToken = connectionSettings?.settings?.access_token || connectionSettings.settings?.oauth?.credentials?.access_token;

  if (!connectionSettings || !accessToken) {
    throw new Error('GitHub not connected');
  }
  return accessToken;
}

async function getUncachableGitHubClient() {
  const accessToken = await getAccessToken();
  return new Octokit({ auth: accessToken });
}

function getAllFiles(dirPath, arrayOfFiles = [], baseDir = null) {
  if (!baseDir) {
    baseDir = dirPath;
  }
  
  const files = readdirSync(dirPath);

  const ignoreDirs = [
    '.git', 'node_modules', '.replit', '.config', '__pycache__', 
    '.upm', 'venv', 'pythonlibs', '.pythonlibs', 'nix', '.cache', 'local'
  ];

  files.forEach(function(file) {
    const fullPath = join(dirPath, file);
    
    if (ignoreDirs.includes(file) || file.startsWith('.')) {
      return;
    }

    try {
      const stats = statSync(fullPath);
      
      if (stats.isDirectory()) {
        arrayOfFiles = getAllFiles(fullPath, arrayOfFiles, baseDir);
      } else if (stats.isFile()) {
        const relativePath = relative(baseDir, fullPath);
        arrayOfFiles.push(relativePath);
      }
    } catch (err) {
    }
  });

  return arrayOfFiles;
}

async function pushToGithub() {
  try {
    console.log('Conectando ao GitHub...');
    const octokit = await getUncachableGitHubClient();
    
    const owner = '22ez0';
    const repo = 'telegram-spotify-bot';
    const branch = 'main';
    
    console.log('Lendo arquivos locais...');
    const files = getAllFiles('.');
    
    console.log(`Encontrados ${files.length} arquivos para commit`);
    
    let uploadedCount = 0;
    for (const file of files) {
      try {
        const content = readFileSync(file);
        const base64Content = content.toString('base64');
        
        await octokit.repos.createOrUpdateFileContents({
          owner,
          repo,
          path: file,
          message: `Add ${file}`,
          content: base64Content,
          branch: branch
        });
        
        uploadedCount++;
        if (uploadedCount % 5 === 0 || uploadedCount === files.length) {
          console.log(`  Enviado ${uploadedCount}/${files.length} arquivos...`);
        }
      } catch (err) {
        console.log(`Erro ao enviar ${file}: ${err.message}`);
      }
    }
    
    console.log('✅ Push realizado com sucesso!');
    console.log(`Total de arquivos enviados: ${uploadedCount}/${files.length}`);
    
  } catch (error) {
    console.error('❌ Erro ao fazer push:', error.message);
    throw error;
  }
}

pushToGithub();
