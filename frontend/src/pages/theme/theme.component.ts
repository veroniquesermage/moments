import {Component, OnInit} from '@angular/core';
import {AVAILABLE_THEMES} from 'src/core/theme/theme.config';
import {ThemeService} from 'src/core/services/theme.service';
import {ThemeMeta} from 'src/core/theme/theme.types';
import {FormsModule} from '@angular/forms';
import {NgClass, NgForOf} from '@angular/common';
import {Router} from '@angular/router';

@Component({
  selector: 'app-theme',
  standalone: true,
  imports: [
    FormsModule,
    NgClass,
    NgForOf
  ],
  templateUrl: './theme.component.html',
  styleUrl: './theme.component.scss'
})
export class ThemeComponent implements OnInit {
  themes: ThemeMeta[] = AVAILABLE_THEMES;
  selectedTheme!: string;

  constructor(private themeService: ThemeService,
              private router : Router) {}

  ngOnInit(): void {
    this.selectedTheme = this.themeService.current;
  }

  onThemeChange(themeValue: string): void {
    this.themeService.setTheme(themeValue as any);
    this.selectedTheme = themeValue;
    void this.router.navigate(['/dashboard']);
  }

  return() {
    void this.router.navigate(['/dashboard']);
  }
}
