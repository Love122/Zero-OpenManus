/**
 * 多语言支持模块
 */

// 翻译数据
const translations = {
    // 中文（简体）
    'zh-CN': {
        'app_title': 'OpenManus',
        'app_subtitle': 'AI智能助手 - 网页版',
        'processing_progress': '处理进度',
        'ai_thinking_process': 'AI思考过程',
        'records_count': '0 条记录',
        'auto_scroll': '自动滚动',
        'clear': '清空',
        'workspace_files': '工作区文件',
        'refresh_countdown': '5秒后刷新',
        'refresh': '刷新',
        'conversation': '对话',
        'file_name': '文件名',
        'close': '关闭',
        'input_placeholder': '输入您的问题或指令...（可使用工具命令）',
        'send': '发送',
        'stop': '停止',
        'ui_made_by': 'Web界面制作:',
        'powered_by': 'Powered by OpenManus -',

        // 项目管理相关
        'projects': '项目',
        'new_project': '新建',
        'rename_project': '重命名',
        'delete_project': '删除',
        'sessions': '对话',
        'new_session': '新建',
        'rename_session': '重命名',
        'delete_session': '删除',
        'project_details': '项目详情',
        'save_project': '保存',
        'project_name_placeholder': '项目名称',
        'project_instructions': '项目指示',
        'project_instructions_placeholder': '输入项目指示 - 这些指示将应用于所有对话',
        'confirm_delete_project': '确定要删除这个项目吗？所有相关对话也会被删除。',
        'confirm_delete_session': '确定要删除这个对话吗？',
        'rename_project_prompt': '请输入新的项目名称：',
        'rename_session_prompt': '请输入新的对话名称：',
        'project_saved': '项目已保存',
        'no_project_selected': '未选择项目',

        // 工具相关
        'tool_settings': '工具设置',
    },

    // 英语
    'en-US': {
        'app_title': 'OpenManus',
        'app_subtitle': 'AI Assistant - Web Version',
        'processing_progress': 'Processing Progress',
        'ai_thinking_process': 'AI Thinking Process',
        'records_count': '0 records',
        'auto_scroll': 'Auto-scroll',
        'clear': 'Clear',
        'workspace_files': 'Workspace Files',
        'refresh_countdown': 'Refresh in 5s',
        'refresh': 'Refresh',
        'conversation': 'Conversation',
        'file_name': 'File Name',
        'close': 'Close',
        'input_placeholder': 'Enter your question or instruction... (Tool commands are available)',
        'send': 'Send',
        'stop': 'Stop',
        'ui_made_by': 'Web UI by:',
        'powered_by': 'Powered by OpenManus -',

        // 项目管理
        'projects': 'Projects',
        'new_project': 'New',
        'rename_project': 'Rename',
        'delete_project': 'Delete',
        'sessions': 'Sessions',
        'new_session': 'New',
        'rename_session': 'Rename',
        'delete_session': 'Delete',
        'project_details': 'Project Details',
        'save_project': 'Save',
        'project_name_placeholder': 'Project Name',
        'project_instructions': 'Project Instructions',
        'project_instructions_placeholder': 'Enter project instructions - these will apply to all sessions',
        'confirm_delete_project': 'Are you sure you want to delete this project? All related sessions will also be deleted.',
        'confirm_delete_session': 'Are you sure you want to delete this session?',
        'rename_project_prompt': 'Please enter a new project name:',
        'rename_session_prompt': 'Please enter a new session name:',
        'project_saved': 'Project saved',
        'no_project_selected': 'No project selected',

        // 工具相关
        'tool_settings': 'Tool Settings',
    },

    // 已将原日文翻译为中文
    'ja-JP': {
        'app_title': 'OpenManus',
        'app_subtitle': 'AI智能助手 - 网页版',
        'processing_progress': '处理进度',
        'ai_thinking_process': 'AI思考过程',
        'records_count': '0条记录',
        'auto_scroll': '自动滚动',
        'clear': '清空',
        'workspace_files': '工作区文件',
        'refresh_countdown': '5秒后刷新',
        'refresh': '刷新',
        'conversation': '对话',
        'file_name': '文件名',
        'close': '关闭',
        'input_placeholder': '输入您的问题或指令...（可使用工具命令）',
        'send': '发送',
        'stop': '停止',
        'ui_made_by': 'Web界面制作:',
        'powered_by': '由OpenManus提供支持 -',

        // 项目管理相关
        'projects': '项目',
        'new_project': '新建',
        'rename_project': '重命名',
        'delete_project': '删除',
        'sessions': '对话',
        'new_session': '新建',
        'rename_session': '重命名',
        'delete_session': '删除',
        'project_details': '项目详情',
        'save_project': '保存',
        'project_name_placeholder': '项目名称',
        'project_instructions': '项目指示',
        'project_instructions_placeholder': '输入项目指示 - 这些指示将应用于所有对话',
        'confirm_delete_project': '确定要删除这个项目吗？所有相关对话也会被删除。',
        'confirm_delete_session': '确定要删除这个对话吗？',
        'rename_project_prompt': '请输入新的项目名称：',
        'rename_session_prompt': '请输入新的对话名称：',
        'project_saved': '项目已保存',
        'no_project_selected': '未选择项目',

        // 工具相关
        'tool_settings': '工具设置',
    }
};

// 默认语言
let currentLanguage = 'zh-CN';

/**
 * 设置语言
 * @param {string} language - 语言代码
 */
function setLanguage(language) {
    if (translations[language]) {
        currentLanguage = language;
        updatePageTranslations();
        saveLanguagePreference(language);
        
        // 通知后端语言设置
        fetch('/api/set_language', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ language: language })
        }).catch(error => {
            console.error('更新语言设置时发生错误:', error);
        });
    } else {
        console.error('不支持的语言:', language);
    }
}

/**
 * 保存语言设置
 * @param {string} language - 语言代码
 */
function saveLanguagePreference(language) {
    localStorage.setItem('openmanusLanguage', language);
}

/**
 * 加载保存的语言设置
 * @returns {string} 语言代码
 */
function loadLanguagePreference() {
    return localStorage.getItem('openmanusLanguage') || 'zh-CN';
}

/**
 * 更新页面翻译
 */
function updatePageTranslations() {
    const elements = document.querySelectorAll('[data-i18n]');
    
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[currentLanguage][key]) {
            // 根据标签类型进行不同处理
            if (element.tagName === 'INPUT' && element.type === 'text') {
                element.placeholder = translations[currentLanguage][key];
            } else if (element.tagName === 'TEXTAREA') {
                element.placeholder = translations[currentLanguage][key];
            } else {
                element.textContent = translations[currentLanguage][key];
            }
        }
    });
}

/**
 * 获取指定键对应的翻译文本
 * @param {string} key - 翻译键
 * @returns {string} 翻译文本
 */
function t(key) {
    return translations[currentLanguage][key] || key;
}

/**
 * 从浏览器语言中确定最佳语言
 * @returns {string} 语言代码
 */
function detectBrowserLanguage() {
    const browserLang = navigator.language || navigator.userLanguage;
    
    // 仅获取语言代码的前半部分（例如：'ja-JP' -> 'ja'）
    const langPrefix = browserLang.split('-')[0];
    
    // 从支持的语言中选择最接近浏览器语言的语言
    if (langPrefix === 'zh') {
        return 'zh-CN';
    } else if (langPrefix === 'ja') {
        return 'ja-JP';
    } else {
        return 'en-US'; // 默认
    }
}

/**
 * 初始化处理
 */
function initI18n() {
    // 加载保存的语言设置，若没有则检测浏览器语言
    const savedLanguage = loadLanguagePreference();
    const detectedLanguage = detectBrowserLanguage();
    
    // 设置语言
    setLanguage(savedLanguage || detectedLanguage);
    
    // 语言选择器的事件监听器
    const languageSelector = document.getElementById('language-selector');
    if (languageSelector) {
        languageSelector.value = currentLanguage;
        languageSelector.addEventListener('change', (e) => {
            setLanguage(e.target.value);
        });
    }
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', initI18n);

// 导出
export { setLanguage, t, currentLanguage, initI18n };
