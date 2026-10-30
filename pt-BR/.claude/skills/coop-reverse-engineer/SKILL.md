---
name: coop-reverse-engineer
description: "Fazer engenharia reversa de um jogo ou motor para entender scripts, código de rede, salvamentos e carregamento de fases, usando ferramentas para agentes como REA, GhidraMCP, ida-pro-mcp, Ghidra sem interface, Frida e extratores de dados de motores."
---

<a id="reverse-engineer-the-game-for-co-op"></a>
# Faça engenharia reversa do jogo para modo cooperativo

1. Priorize código-fonte: ports de código aberto, descompilações, scripts distribuídos com o jogo e SDKs.
2. Camada de scripts: encontre ou escreva um leitor de arquivos contêiner, extraia scripts como texto e teste a ida e volta de qualquer empacotador.
3. Camada nativa: peça autorização antes de instalar ferramentas. Opções: REA (`npx rea-agents setup`, executado pelo usuário; depois reinicie o agente), GhidraMCP, ida-pro-mcp ou Ghidra sem interface para descompilar tudo em um arquivo `.c` com índice de funções.
4. Extratores de dados de motores: UE4SS e Dumper-7 para Unreal 4/5; Il2CppDumper ou Cpp2IL para Unity IL2CPP; dnSpyEx para Unity Mono.
5. Mapeie o necessário ao modo cooperativo: código de rede (se houver), onde rodam a história e a IA, o que é exclusivo do cliente (interface, cenas, diálogos), transições de fases e salvamentos e verificações de instância única.
6. Registre assinaturas de bytes para a compilação exata analisada.
7. Mantenha dumps e código descompilado em `local/`. Publique somente descobertas, nomes, offsets e código de sua autoria.

Detalhes: `playbook/reverse-engineering.md`, `playbook/tools.md`.
