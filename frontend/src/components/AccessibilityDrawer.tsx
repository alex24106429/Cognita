import React from 'react';
import {
  Badge,
  Box,
  Button,
  Divider,
  Drawer,
  Group,
  Paper,
  SegmentedControl,
  Select,
  Slider,
  Stack,
  Switch,
  Text,
  Title,
} from '@mantine/core';
import { IconAccessible, IconRefresh, IconTypography } from '@tabler/icons-react';

import type { AccessibilitySettings, ColorTheme, FontFamily, ThemePalette } from '../types';
import { formatBionic } from '../utils/bionic';

interface Props {
  opened: boolean;
  onClose: () => void;
  settings: AccessibilitySettings;
  palette: ThemePalette;
  onUpdateSettings: (settings: AccessibilitySettings) => void;
}

export const DEFAULT_SETTINGS: AccessibilitySettings = {
  fontSize: 18,
  lineHeight: 1.85,
  letterSpacing: 0.05,
  fontFamily: 'Atkinson Hyperlegible',
  colorTheme: 'sepia',
  bionicMode: true,
  focusRuler: false,
};

const FONT_OPTIONS: { value: FontFamily; label: string }[] = [
  { value: 'Atkinson Hyperlegible', label: 'Atkinson Hyperlegible (recommended)' },
  { value: 'OpenDyslexic', label: 'OpenDyslexic' },
  { value: 'Inter', label: 'Inter' },
  { value: 'System', label: 'System default' },
];

const THEME_OPTIONS: { value: ColorTheme; label: string }[] = [
  { value: 'classic', label: 'Classic white' },
  { value: 'sepia', label: 'Cream / sepia (low glare)' },
  { value: 'solarized', label: 'Solarized light' },
  { value: 'dark', label: 'Dark charcoal' },
];

const PREVIEW_TEXT =
  'Deliberate practice requires immediate feedback on performance, not merely accumulated hours.';

export const AccessibilityDrawer: React.FC<Props> = ({
  opened,
  onClose,
  settings,
  palette,
  onUpdateSettings,
}) => {
  const update = <K extends keyof AccessibilitySettings>(
    key: K,
    value: AccessibilitySettings[K]
  ) => onUpdateSettings({ ...settings, [key]: value });

  return (
    <Drawer
      opened={opened}
      onClose={onClose}
      position="right"
      size="md"
      title={
        <Group gap="xs">
          <IconAccessible size={20} color={palette.accent} />
          <Title order={4}>Accessibility & typography</Title>
        </Group>
      }
    >
      <Stack gap="lg">
        <Box>
          <Text size="sm" fw={600} mb={4}>
            <IconTypography size={14} style={{ verticalAlign: '-2px', marginRight: 6 }} />
            Typeface
          </Text>
          <Select
            data={FONT_OPTIONS}
            value={settings.fontFamily}
            onChange={(value) => value && update('fontFamily', value as FontFamily)}
            comboboxProps={{ withinPortal: true }}
            aria-label="Select reading typeface"
          />
          <Text size="xs" c="dimmed" mt={4}>
            Atkinson Hyperlegible is designed by the Braille Institute to maximise character
            distinction (b/d, p/q). OpenDyslexic adds weighted letter bottoms.
          </Text>
        </Box>

        <Divider />

        <Box>
          <Group justify="space-between" mb={4}>
            <Text size="sm" fw={600}>
              Text size
            </Text>
            <Badge size="sm" variant="light">
              {settings.fontSize}px
            </Badge>
          </Group>
          <Slider
            min={14}
            max={28}
            step={1}
            value={settings.fontSize}
            onChange={(value) => update('fontSize', value)}
            marks={[
              { value: 14, label: '14' },
              { value: 18, label: '18' },
              { value: 22, label: '22' },
              { value: 28, label: '28' },
            ]}
            aria-label="Text size in pixels"
          />
        </Box>

        <Box>
          <Group justify="space-between" mb={4}>
            <Text size="sm" fw={600}>
              Line spacing
            </Text>
            <Badge size="sm" variant="light">
              {settings.lineHeight.toFixed(2)}×
            </Badge>
          </Group>
          <Slider
            min={1.4}
            max={2.4}
            step={0.05}
            value={settings.lineHeight}
            onChange={(value) => update('lineHeight', value)}
            marks={[
              { value: 1.8, label: '1.8 (BDA)' },
              { value: 2.4, label: '2.4' },
            ]}
            aria-label="Line height multiplier"
          />
        </Box>

        <Box>
          <Group justify="space-between" mb={4}>
            <Text size="sm" fw={600}>
              Word spacing
            </Text>
            <Badge size="sm" variant="light">
              {settings.letterSpacing.toFixed(2)}em
            </Badge>
          </Group>
          <Slider
            min={0}
            max={0.2}
            step={0.01}
            value={settings.letterSpacing}
            onChange={(value) => update('letterSpacing', value)}
            marks={[
              { value: 0, label: '0' },
              { value: 0.15, label: '0.15 (BDA)' },
            ]}
            aria-label="Letter and word spacing in em"
          />
        </Box>

        <Divider />

        <Box>
          <Text size="sm" fw={600} mb={4}>
            Colour theme
          </Text>
          <SegmentedControl
            fullWidth
            orientation="vertical"
            value={settings.colorTheme}
            onChange={(value) => update('colorTheme', value as ColorTheme)}
            data={THEME_OPTIONS.map((option) => ({
              value: option.value,
              label: option.label,
            }))}
          />
          <Text size="xs" c="dimmed" mt={4}>
            Reducing background luminance contrast helps with scotopic sensitivity and pattern
            glare.
          </Text>
        </Box>

        <Divider />

        <Switch
          checked={settings.bionicMode}
          onChange={(event) => update('bionicMode', event.currentTarget.checked)}
          label="Bionic salience formatting"
          description="Bolds the leading 45% of each word to create fixation points."
        />

        <Switch
          checked={settings.focusRuler}
          onChange={(event) => update('focusRuler', event.currentTarget.checked)}
          label="Reading focus ruler"
          description="Dims everything except the line under your pointer."
        />

        <Box>
          <Text size="sm" fw={600} mb={6}>
            Live preview
          </Text>
          <Paper
            withBorder
            radius="md"
            p="md"
            style={{
              backgroundColor: palette.background,
              borderColor: palette.border,
              color: palette.text,
              fontSize: `${settings.fontSize}px`,
              lineHeight: settings.lineHeight,
              letterSpacing: `${settings.letterSpacing}em`,
            }}
          >
            {settings.bionicMode ? formatBionic(PREVIEW_TEXT) : PREVIEW_TEXT}
          </Paper>
        </Box>

        <Button
          variant="light"
          color="gray"
          leftSection={<IconRefresh size={16} />}
          onClick={() => onUpdateSettings({ ...DEFAULT_SETTINGS })}
        >
          Reset to recommended defaults
        </Button>
      </Stack>
    </Drawer>
  );
};
