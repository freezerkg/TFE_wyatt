namespace Projet2;

partial class LoginForm
{
    private System.ComponentModel.IContainer components = null;
    
    // Éléments d'interface requis
    private System.Windows.Forms.ComboBox userComboBox;
    private System.Windows.Forms.Button loginButton;
    private System.Windows.Forms.Button newUserButton; // Ajout du bouton Nouveau

    protected override void Dispose(bool disposing)
    {
        if (disposing && (components != null))
        {
            components.Dispose();
        }
        base.Dispose(disposing);
    }

    #region Windows Form Designer generated code

    private void InitializeComponent()
    {
        this.userComboBox = new System.Windows.Forms.ComboBox();
        this.loginButton = new System.Windows.Forms.Button();
        this.newUserButton = new System.Windows.Forms.Button();
        this.SuspendLayout();
        
        // userComboBox
        this.userComboBox.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
        this.userComboBox.FormattingEnabled = true;
        this.userComboBox.Location = new System.Drawing.Point(40, 40);
        this.userComboBox.Name = "userComboBox";
        this.userComboBox.Size = new System.Drawing.Size(240, 28);
        this.userComboBox.TabIndex = 0;
        
        // loginButton
        this.loginButton.Location = new System.Drawing.Point(40, 90);
        this.loginButton.Name = "loginButton";
        this.loginButton.Size = new System.Drawing.Size(110, 35);
        this.loginButton.TabIndex = 1;
        this.loginButton.Text = "Se connecter";
        this.loginButton.UseVisualStyleBackColor = true;
        
        // newUserButton
        this.newUserButton.Location = new System.Drawing.Point(170, 90);
        this.newUserButton.Name = "newUserButton";
        this.newUserButton.Size = new System.Drawing.Size(110, 35);
        this.newUserButton.TabIndex = 2;
        this.newUserButton.Text = "Nouveau";
        this.newUserButton.UseVisualStyleBackColor = true;
        
        // LoginForm
        this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 20F);
        this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
        this.ClientSize = new System.Drawing.Size(320, 160);
        this.Controls.Add(this.newUserButton);
        this.Controls.Add(this.loginButton);
        this.Controls.Add(this.userComboBox);
        this.Name = "LoginForm";
        this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
        this.Text = "Suivi Sportif - Connexion";
        this.ResumeLayout(false);
    }

    #endregion
}