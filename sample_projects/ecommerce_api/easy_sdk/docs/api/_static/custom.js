
// Custom JavaScript for Django API Documentation

document.addEventListener('DOMContentLoaded', function() {
    // Add copy to clipboard functionality for code examples
    const codeExamples = document.querySelectorAll('.code-example');
    
    codeExamples.forEach(function(codeBlock) {
        const copyButton = document.createElement('button');
        copyButton.textContent = 'Copy';
        copyButton.className = 'copy-button';
        copyButton.style.cssText = 'position: absolute; top: 0.5rem; right: 0.5rem; padding: 0.25rem 0.5rem; background: #007bff; color: white; border: none; border-radius: 0.25rem; cursor: pointer;';
        
        codeBlock.style.position = 'relative';
        codeBlock.appendChild(copyButton);
        
        copyButton.addEventListener('click', function() {
            navigator.clipboard.writeText(codeBlock.textContent.replace('Copy', '').trim());
            copyButton.textContent = 'Copied!';
            setTimeout(function() {
                copyButton.textContent = 'Copy';
            }, 2000);
        });
    });
    
    // Add collapsible sections for detailed field information
    const fieldSections = document.querySelectorAll('.field-details');
    
    fieldSections.forEach(function(section) {
        const header = section.querySelector('h4, h5, h6');
        if (header) {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                const content = section.querySelector('.field-content');
                if (content) {
                    content.style.display = content.style.display === 'none' ? 'block' : 'none';
                }
            });
        }
    });
});
