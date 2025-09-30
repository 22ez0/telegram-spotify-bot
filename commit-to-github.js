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

async function commitAndPush() {
  try {
    console.log('Conectando ao GitHub...');
    const octokit = await getUncachableGitHubClient();
    
    const owner = '22ez0';
    const repo = 'telegram-spotify-bot';
    const branch = 'main';
    
    let commitSha = null;
    let treeSha = null;
    
    try {
      console.log('Verificando se o branch existe...');
      const { data: refData } = await octokit.git.getRef({
        owner,
        repo,
        ref: `heads/${branch}`
      });
      commitSha = refData.object.sha;
      
      console.log('Obtendo commit base...');
      const { data: commitData } = await octokit.git.getCommit({
        owner,
        repo,
        commit_sha: commitSha
      });
      treeSha = commitData.tree.sha;
    } catch (err) {
      if (err.status === 409 || err.status === 404) {
        console.log('Repositório vazio ou branch não existe. Criando primeiro commit...');
      } else {
        throw err;
      }
    }
    
    console.log('Lendo arquivos locais...');
    const files = getAllFiles('.');
    
    console.log(`Encontrados ${files.length} arquivos para commit`);
    
    const blobs = [];
    let uploadedCount = 0;
    for (const file of files) {
      try {
        const content = readFileSync(file);
        const base64Content = content.toString('base64');
        
        const { data: blobData } = await octokit.git.createBlob({
          owner,
          repo,
          content: base64Content,
          encoding: 'base64'
        });
        
        blobs.push({
          path: file,
          mode: '100644',
          type: 'blob',
          sha: blobData.sha
        });
        uploadedCount++;
        if (uploadedCount % 10 === 0) {
          console.log(`  Uploaded ${uploadedCount}/${files.length} files...`);
        }
      } catch (err) {
        console.log(`Erro ao processar ${file}: ${err.message}`);
      }
    }
    
    if (blobs.length === 0) {
      console.log('❌ Nenhum arquivo válido encontrado para commit');
      return;
    }
    
    console.log(`Criando tree com ${blobs.length} arquivos...`);
    const treeParams = {
      owner,
      repo,
      tree: blobs
    };
    if (treeSha) {
      treeParams.base_tree = treeSha;
    }
    const { data: newTree } = await octokit.git.createTree(treeParams);
    
    console.log('Criando commit...');
    const commitParams = {
      owner,
      repo,
      message: 'Commit automático via Replit Agent',
      tree: newTree.sha
    };
    if (commitSha) {
      commitParams.parents = [commitSha];
    } else {
      commitParams.parents = [];
    }
    const { data: newCommit } = await octokit.git.createCommit(commitParams);
    
    if (commitSha) {
      console.log('Atualizando referência do branch...');
      await octokit.git.updateRef({
        owner,
        repo,
        ref: `heads/${branch}`,
        sha: newCommit.sha
      });
    } else {
      console.log('Criando referência do branch...');
      await octokit.git.createRef({
        owner,
        repo,
        ref: `refs/heads/${branch}`,
        sha: newCommit.sha
      });
    }
    
    console.log('✅ Commit e push realizados com sucesso!');
    console.log(`Commit SHA: ${newCommit.sha}`);
    
  } catch (error) {
    console.error('❌ Erro ao fazer commit:', error.message);
    throw error;
  }
}

commitAndPush();
